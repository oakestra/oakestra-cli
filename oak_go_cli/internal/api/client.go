// Package api provides an authenticated HTTP client for the Oakestra System Manager API.
package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/oakestra/oak-go-cli/internal/config"
)

// ------------------------------------------------------------------
// Token cache (mirrors Python login.py behaviour: re-login if >10s old)
// ------------------------------------------------------------------

var (
	tokenMu    sync.Mutex
	loginToken string
	lastLogin  time.Time
)

func fetchToken(baseURL string) (string, error) {
	tokenMu.Lock()
	defer tokenMu.Unlock()

	if loginToken != "" && time.Since(lastLogin) < 10*time.Second {
		return loginToken, nil
	}

	// Read credentials from config; fall back to defaults if not set.
	cfg, err := config.Load()
	if err != nil {
		return "", fmt.Errorf("loading config for login: %w", err)
	}

	payload := map[string]string{
		"username": cfg.GetUsername(),
		"password": cfg.GetPassword(),
	}
	body, _ := json.Marshal(payload)

	resp, err := http.Post(baseURL+"/api/auth/login", "application/json", bytes.NewReader(body))
	if err != nil {
		return "", unreachableError(baseURL, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		raw, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("login failed (HTTP %d): %s\n%s\nCredentials: %s / ***\nUpdate with: oak config credentials <username> [password]",
			resp.StatusCode, raw, configureHint(baseURL), cfg.GetUsername())
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", fmt.Errorf("parsing login response: %w", err)
	}
	token, ok := result["token"].(string)
	if !ok {
		return "", fmt.Errorf("no 'token' field in login response")
	}

	loginToken = token
	lastLogin = time.Now()
	return token, nil
}

// GetToken returns a valid Bearer token for the system manager, fetching a
// fresh one if the cached token has expired.
func GetToken() (string, error) {
	url, err := config.SystemManagerURL()
	if err != nil {
		return "", err
	}
	return fetchToken(url)
}

func unreachableError(baseURL string, cause error) error {
	return fmt.Errorf(
		"Root Orchestrator not reachable at %s\n"+
			"Make sure Oakestra is running, then configure the address with:\n"+
			"  oak config set system_manager_ip <IP>\n"+
			"(underlying error: %v)",
		baseURL, cause,
	)
}

func configureHint(baseURL string) string {
	return fmt.Sprintf(
		"If the Root Orchestrator is running on a different host, update the address with:\n"+
			"  oak config set system_manager_ip <IP>\n"+
			"(current target: %s)", baseURL,
	)
}

// ------------------------------------------------------------------
// smartUnmarshal handles both direct JSON and JSON-encoded strings.
// Some Oakestra versions wrap the response body in a JSON string
// (e.g. the body is `"[{...}]"` instead of `[{...}]`).
// ------------------------------------------------------------------

func smartUnmarshal(data []byte, v interface{}) error {
	// Fast path: direct unmarshal.
	if err := json.Unmarshal(data, v); err == nil {
		return nil
	}
	// The API may have returned a JSON-encoded string — unwrap and retry.
	var s string
	if err := json.Unmarshal(data, &s); err != nil {
		// Neither approach worked; surface the original parse error.
		return json.Unmarshal(data, v)
	}
	return json.Unmarshal([]byte(s), v)
}

// ------------------------------------------------------------------
// Client
// ------------------------------------------------------------------

// Client is an authenticated HTTP client for the Oakestra API.
type Client struct {
	baseURL string
	http    *http.Client
}

// New creates a Client using the system_manager_ip from the local config.
func New() (*Client, error) {
	url, err := config.SystemManagerURL()
	if err != nil {
		return nil, err
	}
	return &Client{
		baseURL: url,
		http:    &http.Client{Timeout: 30 * time.Second},
	}, nil
}

// Do executes an authenticated HTTP request and returns the raw response body.
func (c *Client) Do(method, endpoint string, body interface{}) ([]byte, error) {
	token, err := fetchToken(c.baseURL)
	if err != nil {
		return nil, err
	}

	var bodyReader io.Reader
	if body != nil {
		data, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("marshalling request body: %w", err)
		}
		bodyReader = bytes.NewReader(data)
	}

	req, err := http.NewRequest(method, c.baseURL+endpoint, bodyReader)
	if err != nil {
		return nil, fmt.Errorf("creating request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	resp, err := c.http.Do(req)
	if err != nil {
		if strings.Contains(err.Error(), "connection refused") ||
			strings.Contains(err.Error(), "no such host") ||
			strings.Contains(err.Error(), "i/o timeout") {
			return nil, unreachableError(c.baseURL, err)
		}
		return nil, fmt.Errorf("%s %s failed: %w", method, endpoint, err)
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("%s %s returned HTTP %d: %s", method, endpoint, resp.StatusCode, string(data))
	}
	return data, nil
}

func (c *Client) Get(endpoint string) ([]byte, error) {
	return c.Do(http.MethodGet, endpoint, nil)
}

func (c *Client) Post(endpoint string, body interface{}) ([]byte, error) {
	return c.Do(http.MethodPost, endpoint, body)
}

func (c *Client) Delete(endpoint string) ([]byte, error) {
	return c.Do(http.MethodDelete, endpoint, nil)
}

// ------------------------------------------------------------------
// Domain types
// ------------------------------------------------------------------

// Application represents an Oakestra application returned by the API.
type Application struct {
	ApplicationID        string   `json:"applicationID"`
	ApplicationName      string   `json:"application_name"`
	ApplicationNamespace string   `json:"application_namespace"`
	ApplicationDesc      string   `json:"application_desc"`
	Microservices        []string `json:"microservices"`
}

// MetricPoint is a single timestamped resource measurement.
type MetricPoint struct {
	Value     string `json:"value"`
	Timestamp string `json:"timestamp"`
}

// ServiceInstance is a single running instance of a service.
// Field names cover both the older and newer Oakestra API versions.
type ServiceInstance struct {
	InstanceNumber  int           `json:"instance_number"`
	Status          string        `json:"status"`
	StatusDetail    string        `json:"status_detail"`
	PublicIP        string        `json:"publicip"` // note: lowercase 'ip' in API
	ClusterID       string        `json:"cluster_id"`
	ClusterLocation string        `json:"cluster_location"`
	HostIP          string        `json:"host_ip"`
	HostPort        int           `json:"host_port"`
	Disk            string        `json:"disk"`
	CPUPercent      string        `json:"cpu_percent"`
	MemoryPercent   string        `json:"memory_percent"`
	CPUHistory      []MetricPoint `json:"cpu_history"`
	MemoryHistory   []MetricPoint `json:"memory_history"`
	Logs            string        `json:"logs"`
	WorkerID        string        `json:"worker_id"`
}

// Service represents a microservice.
// The API uses different field names depending on the endpoint:
//   - /api/services/  uses  application_name / application_namespace
//   - /api/service/{id} uses app_name / app_ns
//
// Both sets are decoded; call GetApplicationName() / GetApplicationNamespace()
// to retrieve the correct value regardless of endpoint.
type Service struct {
	MicroserviceID        string            `json:"microserviceID"`
	MicroserviceName      string            `json:"microservice_name"`
	MicroserviceNamespace string            `json:"microservice_namespace"`
	ApplicationID         string            `json:"applicationID"`
	ApplicationName       string            `json:"application_name"` // list endpoint
	AppName               string            `json:"app_name"`         // detail endpoint
	ApplicationNamespace  string            `json:"application_namespace"`
	AppNs                 string            `json:"app_ns"`
	InstanceList          []ServiceInstance `json:"instance_list"`
	Status                string            `json:"status"`
	StatusDetail          string            `json:"status_detail"`
	// Deployment config (populated on detail endpoint)
	Port           string   `json:"port"`
	Code           string   `json:"code"`
	Virtualization string   `json:"virtualization"`
	Memory         int      `json:"memory"`
	VCPUs          int      `json:"vcpus"`
	VGPUs          int      `json:"vgpus"`
	Environment    []string `json:"environment"`
	RRip           string   `json:"RR_ip"`
}

// GetApplicationName returns the application name regardless of which API
// endpoint populated the struct.
func (s Service) GetApplicationName() string {
	if s.ApplicationName != "" {
		return s.ApplicationName
	}
	return s.AppName
}

// GetApplicationNamespace returns the application namespace.
func (s Service) GetApplicationNamespace() string {
	if s.ApplicationNamespace != "" {
		return s.ApplicationNamespace
	}
	return s.AppNs
}

// ClusterMetricPoint is a single CPU/memory measurement for a cluster.
type ClusterMetricPoint struct {
	Timestamp float64  `json:"timestamp"`
	Value     *float64 `json:"value"` // pointer to handle null entries
}

// Cluster represents a cluster returned by the /api/clusters/ endpoint.
// Port is interface{} because some API versions return it as a string.
type Cluster struct {
	ClusterID       string      `json:"_id"`
	ClusterName     string      `json:"cluster_name"`
	CandidateName   string      `json:"candidate_name"`
	ClusterIP       string      `json:"ip"`
	Port            interface{} `json:"port"`
	Active          bool        `json:"active"`
	ActiveNodes     int         `json:"active_nodes"`
	ClusterLocation string      `json:"cluster_location"`

	// Resource totals
	TotalCPUCores int `json:"total_cpu_cores"`
	TotalGPUCores int `json:"total_gpu_cores"`
	VCPUs         int `json:"vcpus"`
	VGPUs         int `json:"vgpus"`
	MemoryInMB    int `json:"memory_in_mb"`
	VRAM          int `json:"vram"`

	// Current utilisation
	CPUPercent    float64 `json:"cpu_percent"`
	MemoryPercent float64 `json:"memory_percent"`
	GPUPercent    float64 `json:"gpu_percent"`
	GPUTemp       float64 `json:"gpu_temp"`
	VRAMPercent   float64 `json:"vram_percent"`

	// Capabilities
	Virtualization  []string `json:"virtualization"`
	CSIDrivers      []string `json:"csi_drivers"`
	SupportedAddons []string `json:"supported_addons"`
	GPUDrivers      []string `json:"gpu_drivers"`

	LastModifiedTimestamp float64 `json:"last_modified_timestamp"`
}

// PortString returns the cluster port as a printable string regardless of
// whether the API returned it as an int or a string.
func (c Cluster) PortString() string {
	switch v := c.Port.(type) {
	case float64:
		return fmt.Sprintf("%d", int(v))
	case string:
		return v
	case nil:
		return "—"
	default:
		return fmt.Sprintf("%v", v)
	}
}

// ActiveStatus returns a human-readable active/inactive label.
func (c Cluster) ActiveStatus() string {
	if c.Active {
		return "active"
	}
	return "inactive"
}

// ------------------------------------------------------------------
// Application helpers
// ------------------------------------------------------------------

func (c *Client) GetApplications() ([]Application, error) {
	data, err := c.Get("/api/applications")
	if err != nil {
		return nil, err
	}
	var apps []Application
	if err := smartUnmarshal(data, &apps); err != nil {
		return nil, fmt.Errorf("parsing applications: %w", err)
	}
	return apps, nil
}

func (c *Client) GetApplication(appID string) (*Application, error) {
	data, err := c.Get("/api/application/" + appID)
	if err != nil {
		return nil, err
	}
	var app Application
	if err := smartUnmarshal(data, &app); err != nil {
		return nil, fmt.Errorf("parsing application: %w", err)
	}
	return &app, nil
}

func (c *Client) CreateApplication(sla interface{}) ([]Application, error) {
	data, err := c.Post("/api/application", sla)
	if err != nil {
		return nil, err
	}
	var apps []Application
	if err := smartUnmarshal(data, &apps); err != nil {
		return nil, fmt.Errorf("parsing create-application response: %w", err)
	}
	return apps, nil
}

func (c *Client) DeleteApplication(appID string) error {
	_, err := c.Delete("/api/application/" + appID)
	return err
}

// ResolveApplicationID accepts an application ID or name. On name lookup it
// fails if multiple applications share the same name.
func (c *Client) ResolveApplicationID(idOrName string) (*Application, error) {
	// Try direct ID lookup first.
	app, err := c.GetApplication(idOrName)
	if err == nil {
		return app, nil
	}

	// Fall back to name search.
	all, err := c.GetApplications()
	if err != nil {
		return nil, err
	}
	var matches []Application
	for _, a := range all {
		if a.ApplicationName == idOrName {
			matches = append(matches, a)
		}
	}
	switch len(matches) {
	case 0:
		return nil, fmt.Errorf("no application found with ID or name %q", idOrName)
	case 1:
		return &matches[0], nil
	default:
		ids := ""
		for _, m := range matches {
			ids += "\n  " + m.ApplicationID + " (" + m.ApplicationNamespace + ")"
		}
		return nil, fmt.Errorf("multiple applications named %q — use the application ID instead:%s", idOrName, ids)
	}
}

// ------------------------------------------------------------------
// Service helpers
// ------------------------------------------------------------------

func (c *Client) GetService(serviceID string) (*Service, error) {
	data, err := c.Get("/api/service/" + serviceID)
	if err != nil {
		return nil, err
	}
	var svc Service
	if err := smartUnmarshal(data, &svc); err != nil {
		return nil, fmt.Errorf("parsing service: %w", err)
	}
	return &svc, nil
}

// GetAllServices returns all services, optionally filtered by applicationID.
func (c *Client) GetAllServices(appID string) ([]Service, error) {
	endpoint := "/api/services/"
	if appID != "" {
		endpoint += appID
	}
	data, err := c.Get(endpoint)
	if err != nil {
		return nil, err
	}
	var svcs []Service
	if err := smartUnmarshal(data, &svcs); err != nil {
		return nil, fmt.Errorf("parsing services: %w", err)
	}
	// Client-side filter because the endpoint may return more than expected.
	if appID != "" {
		filtered := svcs[:0]
		for _, s := range svcs {
			if s.ApplicationID == appID {
				filtered = append(filtered, s)
			}
		}
		svcs = filtered
	}
	return svcs, nil
}

func (c *Client) DeployInstance(serviceID string) error {
	_, err := c.Post("/api/service/"+serviceID+"/instance", nil)
	return err
}

func (c *Client) UndeployInstance(serviceID string, instanceID int) error {
	endpoint := fmt.Sprintf("/api/service/%s/instance/%d", serviceID, instanceID)
	_, err := c.Delete(endpoint)
	return err
}

// ResolveServiceID accepts a service ID or name. On name lookup it fails if
// multiple services share the same name.
func (c *Client) ResolveServiceID(idOrName string) (*Service, error) {
	// Try direct ID lookup first.
	svc, err := c.GetService(idOrName)
	if err == nil {
		return svc, nil
	}

	// Fall back to name search.
	all, err := c.GetAllServices("")
	if err != nil {
		return nil, err
	}
	var matches []Service
	for _, s := range all {
		if s.MicroserviceName == idOrName {
			matches = append(matches, s)
		}
	}
	switch len(matches) {
	case 0:
		return nil, fmt.Errorf("no service found with ID or name %q", idOrName)
	case 1:
		return &matches[0], nil
	default:
		ids := ""
		for _, m := range matches {
			ids += "\n  " + m.MicroserviceID + " (" + m.GetApplicationName() + ")"
		}
		return nil, fmt.Errorf("multiple services named %q — use the service ID instead:%s", idOrName, ids)
	}
}

// ------------------------------------------------------------------
// Cluster helpers
// ------------------------------------------------------------------

func (c *Client) GetClusters(all bool) ([]Cluster, error) {
	endpoint := "/api/clusters/"
	if !all {
		endpoint += "active"
	}
	data, err := c.Get(endpoint)
	if err != nil {
		return nil, err
	}
	var clusters []Cluster
	if err := smartUnmarshal(data, &clusters); err != nil {
		return nil, fmt.Errorf("parsing clusters: %w", err)
	}
	return clusters, nil
}

// FindCluster returns the cluster matching nameOrID (cluster_name or _id).
func (c *Client) FindCluster(nameOrID string) (*Cluster, error) {
	all, err := c.GetClusters(true)
	if err != nil {
		return nil, err
	}
	for i, cl := range all {
		if cl.ClusterName == nameOrID || cl.ClusterID == nameOrID || cl.CandidateName == nameOrID {
			return &all[i], nil
		}
	}
	return nil, fmt.Errorf("cluster %q not found", nameOrID)
}
