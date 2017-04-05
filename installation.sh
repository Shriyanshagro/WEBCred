# These are all python librabries to install prior to deploy

# install python lib
# sudo pip install sys
sudo pip install extraction
sudo pip install requests
# sudo pip install urllib
# sudo pip install socket
sudo pip install utils
sudo pip install wtforms
# sudo pip install re
# sudo pip install urllib2
# sudo pip install json
# sudo pip install bs4
# sudo pip install unicodedata
# sudo pip install os
# sudo pip install urlparse
# sudo pip install bs4
# done

# install flask
# https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps#step-three-%E2%80%93-install-flask
sudo pip install virtualenv
sudo virtualenv venv
source venv/bin/activate
sudo pip install Flask
deactivate #To deactivate the environment
# done

# install nltk
  # http://www.nltk.org/install.html
  sudo pip install -U nltk
  # nltk.download('all')
# done

# install node js
sudo add-apt-repository ppa:chris-lea/node.js
sudo apt-get update
sudo apt-get install nodejs
# done

#install npm
sudo apt-get install npm
#done

# install phantomjs
sudo npm install phantomjs
# done
