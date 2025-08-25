#Step 1:
#Check permission to run create_lambda_layer.sh
echo "Checking permissions to run this script: create_lambda_layer.sh"
chmod 744 create_lambda_layer.sh
echo
#Create Python virtual environment
echo "Creating python virtual environment."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d'.' -f1,2)
py -$PYTHON_VERSION -m venv create_layer
echo
echo "Success!"
echo
#Step 2:
# Check the operating system
echo "Starting activation of python virtual environment."
echo
echo "Checking operating system."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo
    echo "Running on Windows"
    # Windows-specific commands
    echo
    echo "Executing Windows-specific commands..."
    echo
    # Add your Windows-specific command here
    source create_layer/scripts/activate && echo "Windows: python virtual environment activated."
else
    echo
    echo "Running on Unix/Linux/macOS"
    # Unix/Linux/macOS-specific commands
    echo
    echo "Executing Unix/Linux/macOS-specific commands..."
    # Add your Unix/Linux/macOS-specific command here
    source create_layer/bin/activate && echo "Unix/Linux/macOS: python virtual environment activated."
fi
echo
echo "Success!"
echo
#Step 3:
echo "Starting platform/architecture options for your Lambda Layer."
echo
echo "Note: the Lambda function's platform/architecture that you had chosen on AWS must be the same platform/architecture used for your Lambda Layer that you are currently creating."
echo
echo "Select the platform/architecture you want to target for your Lambda Layer:"
echo "1) Linux x86_64 (manylinux2014_x86_64)"
echo "2) Linux ARM64 (manylinux2014_aarch64)"
read -p "Enter the number corresponding to your choice: " PLATFORM_CHOICE
# Determine the platform based on user input
case $PLATFORM_CHOICE in
    1)
        PLATFORM_TYPE="x86_64"
        PLATFORM="manylinux2014_x86_64"
        ;;
    2)
        PLATFORM_TYPE="ARM64"
        PLATFORM="manylinux2014_aarch64"
        ;;
    *)
        echo "Invalid choice. Please select either 1 or 2. Exiting."
        exit 1
        ;;
esac
echo
# Confirm platform and execute the pip command
echo "You selected platform: $PLATFORM"
echo
echo "Running pip install command..."
pip install --platform $PLATFORM --only-binary=:all: -r requirements.txt --target ./create_layer/Lib/site-packages
echo
# Check if the command was successful
if [[ $? -eq 0 ]]; then
    echo "Dependencies installed successfully for platform: $PLATFORM"
else
    echo "An error occurred while installing dependencies for platform: $PLATFORM"
fi
echo
#Step 4
echo "Starting Lambda Layer folder to be uploaded to Lambda Layer on AWS."
mkdir -p python/lib/python$PYTHON_VERSION
echo
echo "Success!"
echo
echo "Copy and pasting site packages to python directory."
cp -r create_layer/lib/site-packages python/lib/python$PYTHON_VERSION
echo
echo "Success!"
echo
echo "Zip python directory. This zipped folder will be uploaded to a your Lambda Layer. "
zip -r lambda_layer.zip python
echo
echo "Success!"
echo
echo "***********************************************************************************************************"
echo "Note: If zip prompt does not work, just zip the python folder that was created earlier."
echo "You will know if the zip prompt failed because a zipped python folder will be missing from the directory."
echo "***********************************************************************************************************"
echo 
echo "Lastly, follow the instructions."
echo "Step 1: Log into AWS: https://aws.amazon.com/free/?gclid=Cj0KCQiAkJO8BhCGARIsAMkswyhEXAxJZJmQc3j9TJkeV-Pmh3wsLNXS5jVPIf0ZWGJ01TEmJFFXoXEaAvj_EALw_wcB&trk=78b916d7-7c94-4cab-98d9-0ce5e648dd5f&sc_channel=ps&ef_id=Cj0KCQiAkJO8BhCGARIsAMkswyhEXAxJZJmQc3j9TJkeV-Pmh3wsLNXS5jVPIf0ZWGJ01TEmJFFXoXEaAvj_EALw_wcB:G:s&s_kwcid=AL!4422!3!432339156168!e!!g!!aws%20console!9572385111!102212379247&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all"
echo "Step 2: Go to lambda service."
echo "Step 3: Under additional resources, click on Layers."
echo "Step 4: Click on Create Layer button."
echo "Step 5: Type in your layer name. This can be anything."
echo "Step 6: Upload the zipped python that was created earlier."
echo "Step 7: Choose compatible architectures. The platform/architecture you had chosen earlier: $PLATFORM_TYPE"
echo "Step 8: Choose runtime. The runtime you chose earlier: python$PYTHON_VERSION"
echo "Step 9: Click create button."
echo "Step 10: Go to your lambda function. Assuming that you created it. Scroll down to the Layers section."
echo "Step 11: Click Add a Layer button"
echo "Step 12: Under Choose Layer section. Choose Custom Layers."
echo "Step 13: Click on the Custom Layers dropdown box. Choose name of the layer that you had created earlier."
echo "Step 14: Click on the Add button"