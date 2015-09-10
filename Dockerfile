############################################################
# Dockerfile to build 2weeks App
# Based on Ubuntu
# This is the Devlopement Build
############################################################

# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Robert Donovan <admin@mixfin.com>

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list and  Install basic applications
RUN apt-get update && apt-get install -y tar git curl nano wget dialog net-tools build-essential nginx

sudo service nginx start

# openssh-server

# For debugging
#RUN apt-get install -y gdb strace

# Set up DevUser
RUN useradd dlkrbd -u 1000 -s /bin/bash --no-create-home

# Commit out the SSH just to make the file run first
# Create SSHD
#RUN mkdir /var/run/sshd
#RUN echo 'root:screencast' | chpasswd
#RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
#RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
#ENV NOTVISIBLE "in users profile"
#RUN echo "export VISIBLE=now" >> /etc/profile

#Working Dir
#WORKDIR /home/dlkrbd/
#ENV HOME /home/dlkrbd
#VOLUME ["/home"]



#
# Install Python and Basic Python Tools
#
RUN apt-get install -y python python-dev python-distribute python-pip libmysqlclient-dev


# Copy the application folder inside the container
RUN git clone https://github.com/mixfinancial/2Weeks.git

# Get pip to download and install requirements:
RUN pip install -r /requirements.txt

#Run the setup script from Dave
#RUN chmod +x /2Weeks/scripts/bootstrap.sh

#Rerun the Update to resolve install issues
RUN apt-get update

# Expose ports
EXPOSE 8080

# Set the default command to execute when creating a new container
#CMD ["/usr/sbin/sshd", "-D"] && python twoweeks.py
CMD python runserver.py