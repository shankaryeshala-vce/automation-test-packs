cd
rm auto-framework.zip
wget http://ci-build.mpe.lab.vce.com:8080/view/All/job/auto-framework-zip.pytest/ws/auto-framework.zip
chmod +x auto-framework.zip
mkdir -p $AF_BASE_PATH
unzip -o auto-framework.zip -d $AF_BASE_PATH
. $AF_BASE_PATH/env_setup/af_setup.sh
