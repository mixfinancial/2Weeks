############################################################
# Dockerfile to build 2weeks App
# Based on Ubuntu
##d
############################################################

# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Robert Donovan <admin@mixfin.com>

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip

# Copy the application folder inside the container
RUN git clone https://github.com/mixfinancial/2Weeks.git

# Get pip to download and install requirements:
RUN pip install -r /2Weeks/requirements.txt

#Run the setup script from Dave
RUN chmod +x /2Weeks/scripts/bootstrap.sh

#Start up MongoDB
RUN sudo service mongod start

# Expose ports
EXPOSE 80

# Set the default directory where CMD will execute
WORKDIR /2weeks

# Set the default command to execute when creating a new container
# i.e. using CherryPy to serve the application
CMD python twoweeks.py
