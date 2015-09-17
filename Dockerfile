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
RUN apt-get install -y -f tar git curl nano wget dialog nginx supervisor net-tools build-essential python-software-properties software-properties-common

# Install Python and Basic Python Tools
RUN apt-get install -y -f python python-dev python-distribute python-pip libmysqlclient-dev python2.7-dev

#Install webserver and Web server gateway

RUN sudo pip install uwsgi

# install nginx
run apt-get install -y python-software-properties
run apt-get update
RUN add-apt-repository ppa:nginx/stable

# Set up DevUser
RUN useradd dlkrbd -u 1000 -s /bin/bash --no-create-home
RUN gpasswd -a dlkrbd sudo

# Copy the application folder inside the container
RUN git clone https://github.com/mixfinancial/2Weeks.git

# Setup all the config files
run echo "daemon off;" >> /etc/nginx/nginx.conf
run rm /etc/nginx/sites-enabled/default
RUN rm -v /etc/nginx/nginx.conf
run ln -s /home/docker/code/nginx-app.conf /etc/nginx/sites-enabled/
run ln -s /home/docker/code/supervisor-app.conf /etc/supervisor/conf.d/

# Get pip to download and install requirements:
RUN pip install -r /2Weeks/requirements.txt

#Run the setup script from Dave
#RUN chmod +x /2Weeks/scripts/bootstrap.sh


#Rerun the Update to resolve install issues
#RUN apt-get update -f

# Expose ports
EXPOSE 8080

# Set the default command to execute when creating a new container
#CMD ["/usr/sbin/sshd", "-D"] && python twoweeks.py
#CMD python runserver.py
CMD ["supervisord", "-n"]