# AID

## SETUP:

1. Clone the repo locally
   - 1.1 Install git: 
     - Windows: https://git-scm.com/download/win
     - Packet manager: apt isntall git
     
   ```
   $ git clone https://github.com/Hyyy6/AID.git
   $ cd AID
   ```

2. Install Python3.
   - 2.1 Windows: https://www.python.org/downloads/windows/
   - 2.2 Packet manager: apt install python3
   
   ```
   $ python --version
     Python 3.9.2
   ```

3. Create python virtual environment

   ```
   $ python3 -m venv .venv
   $ . .venv/bin/activate
   ```

4. Install required packages and set environment

    ```
    (.venv) $ pip install -r requirements.txt
    (.venv) $ export OPENAI_API_KEY=<YOUR API SECRET KEY>
    ```

5. Run

   ```
   #### initialize empty database
   (.venv) $ flask --app webapp init-db
   #### export required environment variables, e.g.
   (.venv) $ . env_var.sh
   #### run the app. Options --debug, --host=<ip addr>
   (.venv) $ flask --app webapp run 
   ```

