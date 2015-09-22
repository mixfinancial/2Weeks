from twoweeks import app
import twoweeks.config as config

app.run(debug=config.DEBUG, host=config.HOST)