*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Open Test Browser
Suite Teardown  Close all browsers

*** Variables ***

${responsible_selector} =  #form-widgets-responsible
${add_button_selector} =  //button[@name="from2toButton"]

*** Test cases ***

Test Workflow
    Log In  manager  manager
    Goto Homepage
    Add Task Panel  Tasks  manager  AuthenticatedUsers
    Log Out

    Log In  user1  user1
    Goto Homepage
    Click Link  Tasks
    Add Task  First Task  user2  High
    Log Out

    Log In  user2  user2
    Goto Homepage
    Click Link  Tasks
    Add Task  Second Task  user1  Low
    Log Out

    Log In  user1  user1
    Goto Homepage
    Click Link  Tasks
    Click Link  First Task
    Add Response  assign  user2  High
    Log Out

    Goto Homepage
    Log In  user2  user2
    Click Link  Tasks
    Click Link  Second Task
    Add Response  assign  user1  Low

*** Keywords ***

Add Task Panel
    [arguments]  ${title}  ${responsible}  ${can_add_tasks}

    Open Add New Menu
    Click Link  css=a#taskpanel
    Page Should Contain  Add Task Panel
    Input Text  css=input#form-widgets-IBasic-title  ${title}
    Select From List  css=#form-widgets-responsible  ${responsible}
    Select From List  css=#form-widgets-can_add_tasks-from  ${can_add_tasks}
    Click Button  xpath=${add_button_selector}
    Click Button  Save
    Page Should Contain  Item created

Add Task
    [arguments]  ${title}  ${responsible}  ${priority}

    Open Add New Menu
    Click Link  css=a#task
    Page Should Contain  Add Task
    Input Text  css=input#form-widgets-title  ${title}
    Select From List  css=#form-widgets-responsible  ${responsible}
    Select From List  xpath=//select[@name="form.widgets.priority:list"]  ${priority}
    Click Button  Save
    Page Should Contain  Item created

Add Response
    [arguments]  ${state}  ${responsible}  ${priority}

    Select From List  xpath=//select[@name="transition"]  ${state}
    Select From List  xpath=//select[@name="responsible"]  ${responsible}
    Select From List  xpath=//select[@name="priority:int"]  ${priority}
    Click Button  Submit
    Page Should Contain  Added by
