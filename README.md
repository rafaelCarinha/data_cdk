
# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls --context environment=DEV --profile waymark`          list all stacks in the app
 * `cdk diff --context environment=DEV`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation 
 * `cdk bootstrap --context environment=DEV --profile waymark` Bootstraps CloudFormation
 * `cdk deploy --all --context environment=DEV --profile waymark` Deploy all the Stacks in the profile for the DEV environment
 * `cdk deploy DEV-Waymark-Data-AthenaStack --context environment=DEV --profile waymark` Deploy the Athena Stack
 * `cdk deploy DEV-Waymark-Data-VPCStack --context environment=DEV --profile waymark` Deploy the VPC Stack


Enjoy!
