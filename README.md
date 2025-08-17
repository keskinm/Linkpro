Install firefox ESR

```
sudo apt update
sudo apt install -y libnss3 libasound2 libx11-xcb1 libxcb1 libxcomposite1 \
  libxrandr2 libxi6 libgtk-3-0 libgbm1 libdbus-glib-1-2

cd /opt
sudo wget -O /tmp/firefox-esr.tar.bz2 "https://download.mozilla.org/?product=firefox-esr-latest-ssl&os=linux64&lang=en-US"
sudo tar -xjf /tmp/firefox-esr.tar.bz2
sudo mv firefox firefox-esr

sudo ln -sf /opt/firefox-esr/firefox /usr/local/bin/firefox-esr

which firefox-esr && firefox-esr --version
```
