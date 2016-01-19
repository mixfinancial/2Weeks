from twoweeks import application as application
import twoweeks.config as config

########
# main #
########
if __name__ == "__main__":
    application.run(debug=config.DEBUG)