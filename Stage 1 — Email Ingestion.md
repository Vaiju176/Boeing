Stage 1 — Email Ingestion
Technical User Flow
This is the technical user flow for Stage 1. It keeps the updated architecture as the basis and includes the IAM, networking, database, synchronization, failure handling, and idempotency details discussed.
STAGE 1 — EMAIL INGESTION
══════════════════════════════════════════════════════════════════

Supplier / Vendor
        │
        │ Sends payment query email
        ▼
Microsoft 365 Mailbox
        │
        │ Email remains in mailbox until scheduled ingestion
        │
        │
EventBridge Scheduler
        │
        │ 1. Invoke Email Ingestion Lambda
        │
        │    IAM:
        │    lambda:InvokeFunction
        │
        │    Role:
        │    EventBridge Scheduler Execution Role
        ▼
Email Ingestion Lambda
        │
        │
        ├──── 2. Read previous successful Graph Sync State
        │         │
        │         │ PostgreSQL connection
        │         │ TCP 5432
        │         ▼
        │      RDS Proxy
        │         │
        │         ▼
        │      Aurora PostgreSQL
        │
        │      Purpose:
        │      "Where did my previous successful
        │       Microsoft Graph synchronization stop?"
        │
        │      Example:
        │      Previous committed state = STATE-A
        │
        │      IAM:
        │      • Depends on DB authentication design
        │      • rds-db:connect IF IAM DB authentication is used
        │
        │      
        │
        ├──── 3. Retrieve Microsoft Graph credentials
        │         │
        │         ▼
        │      AWS Secrets Manager
        │         │
        │         │ IAM:
        │         │ secretsmanager:GetSecretValue
        │         │
        │         └────────► AWS KMS
        │
        │                    Purpose:
        │                    Protect/decrypt secret
        │
        │                    IAM:
        │                    kms:Decrypt
        │                    where applicable for CMK
        │
        ├──── 4. Authenticate & call Microsoft Graph
        │         │
        │         │ Uses saved STATE-A
        │         │
        │         ▼
        │      NAT Gateway
        │         │
        │         ▼
        │      Internet Gateway
        │         │
        │         ▼
        │      Microsoft Graph
        │         │
        │         ▼
        │      Microsoft 365 Mailbox
        │
        │      AWS IAM for Graph:
        │      N/A
        │
        │      Microsoft side:
        │      Entra ID / Graph application permissions
        │
        │◄──── 5. Receive new / changed emails
        │
        │      Example:
        │      MSG-001   09:01
        │      MSG-002   09:03
        │      MSG-003   09:04
        │
        │      Graph also eventually provides:
        │      Next Sync State = STATE-B
        │
        ├──── 6. Persist required email information
        │         │
        │         ▼
        │      RDS Proxy
        │         │
        │         ▼
        │      Aurora PostgreSQL
        │
        │      Example information:
        │      • Message ID
        │      • Conversation ID
        │      • Received date/time
        │      • Sender
        │      • Recipient
        │      • Subject
        │      • Body / required email context
        │      • Has attachment
        │      • Attachment metadata/reference as applicable
        │      • Processing status
        │
        │      IDEMPOTENCY CHECK:
        │      Message ID is used as the unique
        │      identity of an individual email.
        │
        │      MSG-001 already exists?
        │             │
        │        ┌────┴────┐
        │       YES        NO
        │        │          │
        │     Don't      Persist
        │     duplicate   MSG-001
        │
        ├──── 7. Validate safe persistence
        │
        │      MSG-001 → persisted ✓
        │      MSG-002 → persisted ✓
        │      MSG-003 → persisted ✓
        │
        │              ↓
        │
        │      All required ingestion data
        │      safely persisted?
        │
        │         ┌────┴────┐
        │        YES        NO
        │         │          │
        │         ▼          ▼
        │      Continue    Do NOT advance
        │                  sync state
        │
        ├──── 8. Commit new Graph Sync State
        │         │
        │         ▼
        │      Aurora PostgreSQL
        │
        │      OLD:
        │      STATE-A
        │
        │      NEW:
        │      STATE-B
        │
        │      STATE-B now becomes the
        │      last successfully committed
        │      synchronization state.
        │
        │      PostgreSQL permissions:
        │      INSERT / UPDATE as required
        │
        └──── 9. Start Step Function 1
                  │
                  │ IAM:
                  │ states:StartExecution
                  │
                  │ Role:
                  │ Email Ingestion Lambda
                  │ Execution Role
                  ▼
             Step Function 1

══════════════════════ STAGE 1 ENDS ═════════════════════════
1. EventBridge Scheduler → Email Ingestion Lambda
The supplier does not directly trigger AWS.
For example, three suppliers could send emails between 9:00 and 9:05:
09:01 → MSG-001
09:03 → MSG-002
09:04 → MSG-003
Those emails sit in the Microsoft 365 mailbox.
At the configured schedule, EventBridge Scheduler invokes the Email Ingestion Lambda.
The Scheduler's execution role therefore needs:
Action:
lambda:InvokeFunction
Resource:
<Email-Ingestion-Lambda-ARN>
We should restrict the resource to this particular Lambda rather than granting lambda:*.
2. Lambda → Aurora: Read Previous Graph Sync State
The first important question for Lambda is:
“Where did I finish my previous successful mailbox synchronization?”
Suppose Aurora contains:
Mailbox                 Graph Sync State
─────────────────────   ────────────────
payment@company.com     STATE-A
Think of STATE-A as a bookmark.
Lambda retrieves that state through the database connection:
Lambda
  ↓
RDS Proxy
  ↓
Aurora PostgreSQL
SELECT saved Graph sync state
We deliberately call this sync state, not simply “last successful timestamp.” Microsoft Graph incremental synchronization can use its delta synchronization state.
Permissions
There are three different controls here:
NETWORK
Lambda SG
   ↓ TCP 5432
RDS Proxy SG
   ↓
Aurora SG
AUTHENTICATION
DB credentials
OR
IAM DB Authentication
DATABASE AUTHORIZATION
PostgreSQL SELECT permission
If IAM database authentication is selected:
AWS IAM:
rds-db:connect
If username/password-based authentication is selected, the database credentials will typically be obtained securely rather than hard-coded.
Client decision/TBD: Final Aurora authentication method.
3. Lambda → Secrets Manager → KMS
Lambda needs credentials/configuration for Microsoft Graph authentication.
It requests them from Secrets Manager:
Email Ingestion Lambda
        │
        │ GetSecretValue
        ▼
Secrets Manager
        │
        │ Secret protected using KMS
        ▼
KMS
        │
        ▼
Secrets Manager
        │
        │ Returns secret
        ▼
Lambda
For example, depending on the client's Microsoft authentication design, the secret could contain information such as tenant/application credentials.
Lambda requires:
secretsmanager:GetSecretValue
restricted to the appropriate project secret.
If a customer-managed KMS key is used, the required KMS authorization must also be configured appropriately, including kms:Decrypt where applicable.
An important distinction:
Normally:
Lambda → Secrets Manager
           ↓
          KMS
We shouldn't automatically describe this as Lambda independently calling KMS unless the application actually makes a direct KMS API call.
4. Lambda → Microsoft Graph → Microsoft 365
Now Lambda has:
Previous Graph state = STATE-A
Graph authentication information
It can authenticate to Microsoft Graph and continue the mailbox synchronization.
Because this is an external Microsoft service, the private Lambda's controlled egress path is:
Private Lambda
      ↓
NAT Gateway
      ↓
Internet Gateway
      ↓
Microsoft Graph
      ↓
Microsoft 365 Mailbox
This is why having AWS VPC endpoints later doesn't eliminate our need for internet egress to Microsoft Graph.
AWS IAM doesn't grant permission to read Outlook mail.
That permission belongs on the Microsoft side:
Microsoft Entra ID
       +
Microsoft Graph permissions
The exact Graph permission model remains something we should confirm with the client rather than invent.
5. Microsoft Graph → Lambda: Return Changes
Using our example, Graph determines what has changed since STATE-A.
It returns the relevant message information:
STATE-A
   ↓
Microsoft Graph
   ↓
MSG-001
MSG-002
MSG-003
+
Next synchronization state = STATE-B
Email information available from Graph can include Message ID, Conversation ID, received time, sender, recipient, subject, body and attachment information.
Now Lambda has work to persist.
6. Lambda → Aurora: Persist Emails
For each email, we need to durably record the information assigned to Stage 1.
Conceptually:
MSG-001
   ↓
Aurora
message_id        = MSG-001
conversation_id   = CONV-100
received_at       = 09:01
sender            = supplier@abc.com
subject           = Payment Status
has_attachment    = true
processing_status = RECEIVED
The exact schema/table/column names are not finalized, so these are conceptual examples.
The attachment binary itself does not belong in Aurora. Attachments belong in S3 and the Attachment Processing Lambda handles them later.
7. Idempotency — Very Important
Idempotency means that processing the same email more than once should not create duplicate business records or incorrectly process it twice.
Microsoft Graph Message ID gives us the identity of the individual email.
The primary idempotency concept is:
Graph Message ID + processing status.
Suppose Aurora already contains:
Message ID    Status
──────────    ────────
MSG-001       RECEIVED
MSG-002       RECEIVED
A retry causes Graph to return:
MSG-001
MSG-002
MSG-003
Before treating each message as new, our application can check its existing processing record.
MSG-001
   ↓
Already exists
   ↓
Do not create duplicate
MSG-002
   ↓
Already exists
   ↓
Do not create duplicate
MSG-003
   ↓
Doesn't exist
   ↓
Persist new record
Ideally, the database design should also enforce uniqueness for the chosen idempotency key rather than relying only on application logic.
Conceptually:
message_id = UNIQUE
So even if two processing attempts race:
Attempt 1 → INSERT MSG-001
Attempt 2 → INSERT MSG-001
the database prevents duplicate records.
Where is idempotency stored?
For our architecture:
             AURORA POSTGRESQL
        Email processing / thread state
                   │
         ┌─────────┴─────────┐
         │                   │
     message_id       processing_status
      MSG-001             RECEIVED
      MSG-002             IN_PROGRESS
      MSG-003             COMPLETED
So Aurora contains the durable information used for the idempotency decision.
8. When do we update STATE-A → STATE-B?
This is the most important reliability part of Stage 1.
Graph gives us:
MSG-001
MSG-002
MSG-003
Next State = STATE-B
We do not immediately say STATE-B is successful merely because Graph returned it.
First, the required ingestion information must be safely persisted.
Successful case
MSG-001 → Aurora ✓
MSG-002 → Aurora ✓
MSG-003 → Aurora ✓
        ↓
Required persistence successful
        ↓
STATE-A
   ↓
STATE-B
        ↓
STATE-B becomes the new
committed synchronization state
Now the next scheduled execution can continue from STATE-B.
Failure example
Suppose:
MSG-001 → Aurora ✓
MSG-002 → Aurora ✓
MSG-003 → Aurora ✗
          Database write failed
Then:
DO NOT COMMIT STATE-B
Aurora continues to treat:
Last successful state = STATE-A
Next Scheduler run:
EventBridge Scheduler
       ↓
Lambda
       ↓
Read STATE-A
       ↓
Graph
Graph may return those messages again.
Suppose:
MSG-001
MSG-002
MSG-003
This is where idempotency protects us:
MSG-001
   ↓
Already persisted
   ↓
Don't duplicate
MSG-002
   ↓
Already persisted
   ↓
Don't duplicate
MSG-003
   ↓
Previous persistence failed
   ↓
Persist/recover it
When the required persistence is finally successful:
MSG-001 ✓
MSG-002 ✓
MSG-003 ✓
     ↓
Commit STATE-B
This is why sync-state management and idempotency work together:
SYNC STATE
prevents us from skipping mailbox changes
              +
IDEMPOTENCY
prevents retries from creating duplicates.
9. Lambda → Step Function 1
Once the email is ready to enter downstream processing, the Email Ingestion Lambda starts Step Function 1.
Email Ingestion Lambda
        │
        │ states:StartExecution
        ▼
Step Function 1
The Lambda execution role therefore needs:
Action:
states:StartExecution
Resource:
<Step-Function-1-ARN>
The workflow input can carry the required case/email context or references to it.
We will define the exact handoff when we start Stage 2, because that's where Step Function 1, attachment processing and the Email Processing Consumer become the focus.
Stage 1 — IAM / Access Matrix
#	Connection	Identity/Role	Required permission/control
1	Scheduler → Lambda	Scheduler execution role	lambda:InvokeFunction
2	Lambda → Aurora/RDS Proxy	Lambda execution role + DB identity	rds-db:connect if IAM DB auth is selected; 
2	DB query	PostgreSQL user	SELECT on required sync-state data
3	Lambda → Secrets Manager	Lambda execution role	secretsmanager:GetSecretValue
3	Secret encryption	Appropriate identity/key policy	kms:Decrypt where applicable with customer-managed KMS key
4	Lambda → Microsoft Graph	Microsoft application identity	Microsoft Graph/Entra permissions — not AWS IAM
4	Lambda → Internet	Network controls	Private subnet → NAT → IGW; outbound HTTPS/443 as approved
6	Email persistence	PostgreSQL user	Required SELECT/INSERT/UPDATE privileges
9	Lambda → Step Function 1	Lambda execution role	states:StartExecution
For the final client policy we should also scope every AWS action to the appropriate resource ARN wherever AWS supports resource-level permissions rather than using "Resource": "*" unnecessarily.
Stage 1 — Summary
EventBridge Scheduler periodically invokes the Email Ingestion Lambda. The Lambda first retrieves the last successfully committed Microsoft Graph synchronization state from Aurora, retrieves the required Graph credentials securely from Secrets Manager, and accesses Microsoft Graph through controlled NAT egress. Graph returns mailbox changes since the previous synchronization state. The Lambda durably records the required email information in Aurora using the Graph Message ID as part of the idempotency mechanism. Only after the required messages are safely persisted do we advance the Graph synchronization state. If persistence fails, we retain the previous state and safely retry; Message-ID-based idempotency prevents duplicate processing. Once the email is ready for downstream processing, Lambda starts Step Function 1.
