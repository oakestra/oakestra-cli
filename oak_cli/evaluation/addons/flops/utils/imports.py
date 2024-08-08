# flake8: noqa
import seaborn as sns
from icecream import ic

from oak_cli.evaluation.addons.flops.utils.data_loading import load_and_prepare_data
from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.keys import *
from oak_cli.evaluation.addons.flops.utils.main import Evaluation, prepare_notebook
from oak_cli.evaluation.addons.flops.utils.special_graphs.auxiliary import *
from oak_cli.evaluation.addons.flops.utils.special_graphs.box_violin_plot import *
from oak_cli.evaluation.addons.flops.utils.special_graphs.line_graphs import *
from oak_cli.evaluation.addons.flops.utils.special_graphs.mb_per_second import *
from oak_cli.evaluation.addons.flops.utils.special_graphs.stage_durations import *
from oak_cli.evaluation.addons.flops.utils.special_graphs.trained_model import *
