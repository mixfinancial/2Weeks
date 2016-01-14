from twoweeks import app as application
import twoweeks.config as config

application.run(debug=config.DEBUG, host=config.HOST)