############################################################
# Dockerfile to build 2weeks App
# Based on Ubuntu
# This is the Devlopement Build
############################################################
# Set the base image to Ubuntu
FROM ubuntu:wily
# Add the application resources URL
#RUN echo "deb http://apt.dockerproject.org/repo/dists/ubuntu-wily/main" > /etc/apt/sources.list

# File Author / Maintainer
MAINTAINER Robert Donovan <admin@mixfin.com>

# Update the sources list and Install basic applications
RUN apt-get update
RUN apt-get install -y build-essential git

RUN apt-get install -y python python-dev python-setuptools
RUN apt-get install -y nginx supervisor
RUN easy_install pip


##RUN apt-get install -y -o Dpkg::Options::="--force-confold" tar curl nano wget dialog nginx supervisor net-tools libxml2-dev libxslt1-dev

# Install Python and Basic Python Tools
#RUN apt-get install -y -f python python-dev python-distribute python-pip libmysqlclient-dev python2.7-dev

#Install webserver and Web server gateway
RUN pip install uwsgi

# install nginx
#run apt-get install -y python-software-properties
RUN apt-get install -y software-properties-common python-software-properties
RUN add-apt-repository ppa:nginx/stable
RUN apt-get install libmysqlclient-dev

# Set up DevUser
RUN useradd dlkrbd -u 1000 -s /bin/bash --no-create-home
RUN gpasswd -a dlkrbd sudo

# Copy the application folder inside the container
RUN git clone https://github.com/mixfinancial/2Weeks.git

# Setup all the config files
run echo "daemon off;" >> /etc/nginx/nginx.conf
run rm /etc/nginx/sites-enabled/default
run ln -s /2Weeks/nginx-app.conf /etc/nginx/sites-enabled/
run ln -s /2Weeks/supervisor-app.conf /etc/supervisor/conf.d/

# Get pip to download and install requirements:
RUN pip install -r /2Weeks/requirements.txt

#Run the setup script from Dave
#RUN chmod +x /2Weeks/scripts/bootstrap.sh


#Rerun the Update to resolve install issues
#RUN apt-get update -f

# Expose ports
EXPOSE 80

# Set the default command to execute when creating a new container
#CMD ["/usr/sbin/sshd", "-D"] && python twoweeks.py
CMD ["supervisord", "-n"]

##CMD cd /2Weeks && git pull && newrelic-admin run-program python runserver.py
##CMD cd /2Weeks && git pull && python wsgi.py