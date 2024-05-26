
# SecureErase

  

SecureErase is a simple and user-friendly application designed to securely overwrites the files to prevent data recovery.

  

![Logo](https://github.com/sdmdg/secure-erase/assets/151946448/93240327-dd76-4a80-8849-24ca14ef6c46)

  

![img_1](https://github.com/sdmdg/secure-erase/assets/151946448/bff078af-eb49-46f5-8dbc-63a3fbf2fccc)

  

---

  

## Features

  

* Batch file secure delete

* Free Space clean

* Different overwrite methods

* Dark mode with a user-friendly UI

  
  

## External Dependencies

  

* PyQt5

* pypiwin32

  

---

  

## Installation

### If your system uses an SSD and has TRIM enabled, then most probably you don't have to use this tool. By default, most SSDs now have the TRIM feature enabled. If you want to check if your SSD has the TRIM feature enabled, you can follow these steps to check if TRIM is enabled in Windows 10/11.

1. Type  **cmd** in the start menu, select  **Command Prompt** from the list, and choose **Run as Administrator**.
2. When the command window pops up, type **`fsutil behavior query disabledeleteNotify`** and hit  **Enter**.
3. If TRIM is enabled, it will display “**DisableDeleteNotify=0**”. Else if the value “**DisableDeleteNotify=1**” is displayed that indicates the TRIM is disabled
  
### If your system uses an SSD and TRIM is not enabled, or if you don't have an SSD, then continue to the installation.

1. Install Python 3.11 or above.

2. Clone the repository to your desired location or download the ZIP and extract it.

3. Recommended: Launch `run.bat`(for Windows). This will set up a new virtual environment and install all dependencies.

  

**Or**

  

- Install dependencies manually using:

```bash

pip install -r requirements.txt

```

- Launch `main.py`.

  
  

**Note:** For enhanced data privacy, the application does not include an auto-update module. Once it installs all dependencies, it operates offline. Please visit [here](https://github.com/sdmdg/secure-erase/) to manually check for and install updates.

  

---

  

## Important Note:

  

-  **The Authors will not be responsible for any kind of loss of data. Under no circumstances shall we be liable or responsible to you or any other person for any damages, loss of any of your useful data by using this Software. Read the [LICENSE](https://github.com/sdmdg/secure-erase/blob/master/LICENSE) for more information.**