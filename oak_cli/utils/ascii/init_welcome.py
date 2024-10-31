# flake8: noqa
from rich.segment import Segment
from rich.style import Style

WELCOME_ASCII_LOGO = """
                                         ░░░░░░░
                                   ░░░░░░░░░░░░░░░░░                   
                               ░░░░░░░░░░░░░░░░░░░░░░              
                            ░░░░░░░░░░░░░░░░░░▒░░░░░░░             
██╗    ██╗███████╗██╗  ░░░░██████╗░██████╗░███╗░░░███╗███████╗    ████████╗ ██████╗ 
██║    ██║██╔════╝██║░░░░░██╔════╝██╔═══██╗████╗░████║██╔════╝    ╚══██╔══╝██╔═══██╗
██║ █╗ ██║█████╗  ██║░░░░░██║░▒░░░██║░░░██║██╔████╔██║█████╗░░       ██║   ██║   ██║
██║███╗██║██╔══╝ ░██║░░░▒░██║░░▒░░██║░▒░██║██║╚██╔╝██║██╔══╝░░░░     ██║   ██║   ██║
╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║░╚═╝░██║███████╗░░░    ██║   ╚██████╔╝
 ╚══╝╚══╝ ╚══════╝╚══════╝░╚═════╝░╚═════╝░╚═╝░▒░▒░╚═╝╚══════╝░░░    ╚═╝    ╚═════╝ 
                ░░░░░░░░░░▒▓▓░░░░▓▓▒▓▓▓▒▓▓▓▓▒▓▓▓░░░░░▒░░░▓▒░░░░░     
                 ░░░░░░▒░░░░▒▓▓░░░▒▓▓▓▓▓▓▓▓░░▓▓▓▓░░▓▓▓▓▒░░░░░░       
                   ░░▒▓░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░░░         
                       ░░░░░░░░░░░▒▓▒▓▓▓▓▓▓▓▒░░░░░░░░░░░           
                                  ▒▓▒▓▓▒▓▓▓▓▒
         ██████╗  █████╗ ██╗  ██╗███████╗███████╗████████╗██████╗  █████╗ 
        ██╔═══██╗██╔══██╗██║ ██╔╝██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗
        ██║   ██║███████║█████╔╝ █████╗▓▓███████╗   ██║   ██████╔╝███████║
        ██║   ██║██╔══██║██╔═██╗ ██╔══╝▓▓╚════██║   ██║   ██╔══██╗██╔══██║
        ╚██████╔╝██║  ██║██║  ██╗███████╗███████║   ██║   ██║  ██║██║  ██║
         ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
                               ▒▓▓▓▓▓▒▓▓▓▓▓▓▒▒                      
                             ▒▒▓▒▓ ▓▓  ▒▒▓▓▓▓▓▒▒▒▒ ▒          
                        ▒▒ ▒▒▒▓▒▒▒▒▓▒▒   ▒▒▒▓▒▓ ▒▒▒▒ ▒             
                       ▒    ▒ ▒▒▒▒   ▒▒ ▒▒  ▒ ▒▒▒▒ ▒▒▒▒               
                               ▒  ▒▒             ▒ ▒   ▒                        

"""

WELCOME_COLOR_MAP = {char: Segment(char, Style.parse("steel_blue")) for char in "║═╗╝╔╚"}
WELCOME_COLOR_MAP.update(
    {
        "░": Segment("░", Style.parse("sea_green3")),
        "█": Segment("█", Style.parse("white")),
    }
)