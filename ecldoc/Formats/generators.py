from .HTML import genHTML
from .TXT import genTXT
from .TEX import genTEX

generators = {
	'html' : genHTML.GenHTML,
	'text' : genTXT.GenTXT,
	'pdf' : genTEX.GenTEX
}
