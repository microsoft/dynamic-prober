## README

by Alejandro Cuevas, t-alejandroc@microsoft.com/acuevasv@andrew.cmu.edu


## Installation and First Steps

#### Installation

```
git clone
cd ./project_folder
pip install -r requirements.txt
python src/main.py
```

#### Environment Variables: API Keys and DB Strings

To begin, make sure you create a `.env` file as such:

```
OPENAIAPIKEY='<org_open_AI_key>'
AZOPENAIAPIKEY='<azure_open_AI_key>'
PERSONALKEY = '<personal_open_AI_key>'
AZENDPOINT='<azure_open_AI_endpoint>'
DBSERVER = 'db_endpoint'
DBDATABASE = 'db_name'
DBUSERNAME = '<db_username>'
DBPASSWORD = '<db_password>'
DBDRIVER = '{ODBC Driver 17 for SQL Server}' # I use the following for Azure DB
DBSECRETKEY = '<secret_key_for_a_DB_deployment>'
LOCAL_DB = <str> # 'True' or 'False'
API_RETRY_DELAY = <int>
API_RETRIES = <int>
API_RETRY_FUNC = <str> # parameters for backoff module and retrying logic
```
And that it's present in your folder `.env` file in your current working directory (wherever you plan on running the application).

For example, if you want to test out and work on the application locally here is an example `.env` file:

```
OPENAIAPIKEY='<your OPENAI API KEY here'
AZOPENAIAPIKEY=''
PERSONALKEY = ''
AZENDPOINT=''
DBSERVER = 'db_endpoint'
DBDATABASE = 'db_name'
DBUSERNAME = 'user'
DBPASSWORD = 'password'
DBDRIVER = '{ODBC Driver 17 for SQL Server}'
DBSECRETKEY = 'lol-what-secret'
LOCAL_DB = True
API_RETRY_DELAY = 5
API_RETRIES = 3
API_RETRY_FUNC = constant
```

Keys and DB strings can be modified in `get_db_credentials()` and `get_api_credentials()` in `util.py`

To set the AI key being used, in `skills.py` check `api_key_type = <api_key_to_use>` and choose one from `['personal', 'azure', 'openai']`.

`LOCAL_DB` defaults to `FALSE` unless we set the environment variable to 'True.' This variable controls whether to use the remote Azure DB or not.

#### Initial Steps

To run the chatbot, there are 2 main things we need to check:
1) Our .env file exists and is parameterized accordingly
    a) For a remote deployment, need to make sure the environment variables are set
    b) We have chosen an appropriate API key and have ensured that it's properly set in `skills.py`
2) Run `python src/main.py` (or with `just`: `just run`)
3) A DB is in place (either locally or remotely)
    a) To create a DB (locally or remotely), we should use the `/init_db` path. For instance, if we have a remote deployment, we set LOCAL_DB to 'False' (or leave it empty). Then when we start the application, we can visit `http://<url_to_application>/init_db`. This will instantiate all the tables as defined in `models.py`

Given a functional API key and DB, the application can be deployed. From this point, the main changes we may want to do are: 1) changing the flow of the conversation, 2) changing the questions, and 3) changing the agents.

Note, for a remote deployment it's important to look at the error handling and/or retry logic defined for `skills/get_module_response()`. This function will handle calls to the GPT endpoint. Using the backoff decorator, for example, to handle retries we need to set a couple of parameters: how many times to retry, how often to retry, etc. These parameters matter especially for remote deployments.


#### Global Variables, Other Parameters, and Harcoded Responses

There are additional parameters at the top of `main.py` that dictate some of the app's functionality. It's important to review these and modify as needed.


#### Deployment on 08/02 to 08/09

The chatbot commit which was deployed for this week of experiments is tagged in the AI4Society_Interns repo as 'chatbot-deployment-0802-0809' and later 'prod-minor-api-timeout-increases.' 


## Operation

#### Architecture

Below is the layout of the project:
- `main.py` contains the Flask application and dictates the flow of the conversation and the functions that are called.
- `skills.py` contains the skill definitions. We use Semantic Kernel skills based on the prompts defined in `prompts.py`. These are then wrapped into an `AIModel` class. Lastly, I call all agents from the `get_model_response()` function. The context is maintained inside the `AIModel` class.
- `prompts.py` contains prompts as constant strings
- `models.py` contains the database schemas using SQLAlchemy and also other useful classes
- `utils.py` contains utility functions for logging and credentials
- `question_bank.py` is where we define the main questions to be used throughout the interview with the chatbot

#### Study Design and Groups

For our study, we used 3 study groups: 'baseline', 'dynamic probing', and 'active listener.'

The study group decision and participant ID from Qualtrics gets passed to the webapp in the following way: http://localhost:5000/user_landing?sg=bs&req=test

- `sg` is the study group, where we choose from either 'bs', 'dp', and 'al', respectively
- `req` is the participant ID variable, such as a numeric string `52345`

If no parameters are set, `sg` defaults to `al` and `req` to `test`.

The participant ID is currently generated in Qualtrics and passed to the application when a used lands in the chatbot. Once the user finishes the study, they receive a code based on the `USER_ID` they were assigned when a new entry for them was created in the DB. We add 10000 to this number to keep it in a range of 10000 to 20000 (to do a light validation on Qualtrics). Having a `USER_ID` and a `PARTICIPANT_ID` allows us to match participants' response on Qualtrics with responses on the chatbot.


#### Conversation Flow and Questions

Currently, the conversation flow is defined in `INTERVIEW_SEQUENCE` as a list of functions. Essentially,
the chatbot will follow the same procedure with each participant; the flow is not altered. I think a good mental model for the flow, is to think of the chatbot as following as script, where each entry in the script is a function that gets called in response to a participant's response. Currently, our script is static (we procedurally cally each function defined in the `INTERVIEW_SEQUENCE` list). However, we can build logic that alters (e.g., branches) what function is called from this list. 

In our application, we call 'main question' the first topic question. That is, in the context of AI alignment, the main question is the question we are interested in hearing a response to. Then, any follow-ups are to further clarify the response we may get to this main question. These main questions can be modified in `question_bank.py`. Currently, we just randomly pick a set of questions that we will ask a participant. Then, we do our follow-ups based on those.

#### Creating or Modifying Agents

To add a new agent, we must follow the following steps:
1) Declaring a skill (see `skill` definitions). E.g.,`interviewer_skill = kernel.create_semantic_function...`
2) Then wrapping it with the `AIModel` class. E.g., `interviewer = AIModel('interviewer', kernel, interviewer_skill)`. Make sure you give it a different module name.
3) "Registering" the function in `skills/get_module_response()`. Note, registering in this case just means adding a conditional which catches the name of the module we are trying to call. We use `get_module_response()` as a wrapper to our skill calls because we can wrap this function with arbitrary error handling logic (e.g., retries with backoff decorator)
4) Creating a function in `main.py` which will retrieve the module response. 
    a) For example, the prober gets called in `engage_prober()` which is called in `get_followup_question()`.

In semantic kernel, inputs to prompts are passed through a context. You can see in the prompts that there are wildcards like `{{$user_input}}`. Currently, I wrap every semantic kernel skill inside an `AIModel` class. You can call the skill by using `AIModel.skill` and set its context with `AIModel.context`. For instance, `interviewer.context['seed_question'] = <question>` is what you would use to set the `seed_question` to a value to pass to the prompt.

I think modularity is extremely important for a multi-agent application. Our functions in `main.py` need to be able to do 3 things: 1) set the correct state for the module of interest, 2) call and receive the raw response from `get_module_response()`, 3) create an entry in the corresponding DB (if needed), 4) update the state as needed, 5) carry out any necessary string manipulations prior to sending the response to the frontend. For these reasons, I typically have a function which is called as part of the interview flow (e.g., `get_followup_question`), a function which will call the necessary module and handle context (e.g., `engage_prober`), and our `get_module_response` function which returns the endppoint result.

If we do not want to change the existing agents and just want to modify their behavior, we can do this by altering their prompt in `prompts.py`

#### Session Variables

We use Flask Session variables to keep track of global values. Anytime an agent needs to refer to something related to the conversation flow (e.g., the current main question, the number of questions asked, etc.) it is likely stored in a session variable (e.g., `session['MAIN_QUESTION_COUNT']`). Note that Flask Session variables don't reset unless you close the window. Simultaneous windows may also run into problems with session variables.


### Common Errors

- If the DB schema changed in a commit. You may get a SQLAlchemy error when it tries to insert a new entry. To fix this, you need to delete the old DB, and recreate the DB.
- If you are using Azure DB, you may get a connection error if your IP is not whitelisted on Azure Portal.
- If you open simultaneous windows or the session was not cleared properly between one chatbot session and the next, you may run into mismatched session variables.

#### Retry Logic with Remote Deployment

During our 08/02 - 08/09 experiment week we noticed heavy latency on the Azure OpenAI endpoint. To address this, we implemented two things: 1) a backoff decorator which retries the `get_module_response` function upon an error, and 2) `asyncio.wait_for(...) ` to timeout a request if too much time had passed. Proper parameterization of these functions is crucial for a functional deployment.

#### Deleting Remote Tables

IF our schema changed or we want to reset the remote DB, we need to drop the tables. To do this, I follow this procedure:
(Note, these steps were taken from: https://stackoverflow.com/questions/34967878/how-to-drop-all-tables-and-reset-an-azure-sql-database)

- Using Azure Data Studio I connect to the remote DB
- Then we open a "New Query" and remove the foreign keys condition using this query:

```
while(exists(select 1 from INFORMATION_SCHEMA.TABLE_CONSTRAINTS where CONSTRAINT_TYPE='FOREIGN KEY'))
begin
 declare @sql nvarchar(2000)
 SELECT TOP 1 @sql=('ALTER TABLE ' + TABLE_SCHEMA + '.[' + TABLE_NAME
 + '] DROP CONSTRAINT [' + CONSTRAINT_NAME + ']')
 FROM information_schema.table_constraints
 WHERE CONSTRAINT_TYPE = 'FOREIGN KEY'
 exec (@sql)
 PRINT @sql
end
```
- Then,  to delete each table (and maintain your EF migration histories if you want) you need to run the following query.
```
while(exists(select 1 from INFORMATION_SCHEMA.TABLES 
             where TABLE_NAME != '__MigrationHistory' 
             AND TABLE_TYPE = 'BASE TABLE'))
begin
 declare @sql nvarchar(2000)
 SELECT TOP 1 @sql=('DROP TABLE ' + TABLE_SCHEMA + '.[' + TABLE_NAME
 + ']')
 FROM INFORMATION_SCHEMA.TABLES
 WHERE TABLE_NAME != '__MigrationHistory' AND TABLE_TYPE = 'BASE TABLE'
exec (@sql)
 /* you dont need this line, it just shows what was executed */
 PRINT @sql
end
```
After this procedure, we need to instantiate the DBs again as defined above.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.