# APIM-AI-Service-Farm
This repo is to demonstrate how we implement manual steps to use APIM as a load balancer to distribute GPT chat/completions calls to two gpt-35-tubo models belonging to different Azure AI services.

We start from the best practice of APIM farming OpenAI endpoint, described in this [document](https://learn.microsoft.com/en-us/samples/azure-samples/openai-apim-lb/openai-apim-lb/). We take the [Manual Steps](https://github.com/azure-samples/openai-apim-lb/blob/main/docs/manual-setup.md).

Here is the note we made in each steps:

Step 1: Provision Azure API Management Instance
- Create a new resource group
- Create an APIM for Developer
- Enable System Managed Identity for the APIM

Step 2 & 3: Provision Azure OpenAI Service Instances
- Provision your Azure AI Service instances.
- Add role assignment of "Cognitive Services OpenAI User" for the APIM SMI.
- Deploy the same models (gpt-35-turbo) and versions (0125) in each instance.
- For each model, set TPM to 1k (to easy the testing)

Step 4: Download and Prepare API Schema
- Download the desired API schema for Azure OpenAI Service [inference.json](https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/AzureOpenAI/inference/preview/2023-12-01-preview/inference.json) to your local machine.
- Update the inferencejson file: Open the local inference.json and update the servers section to:
~~~
  "servers": [
      {
      "url": https://microsoft.com/openai,
      "variables": {
          "endpoint": {
          "default": "itdoesntmatter.openai.azure.com"
          }
      }
      }
  ],
~~~

Step 5: Create the API
- Go to your API Management instance in the Azure Portal.
- Under API, click + Add API and select OpenAI with the following fields:
~~~
Display Name=Azure OpenAI Service API
Name=xjxaifiramapim
API URL Suffix=openai-load-balancing/openai
~~~
- Load your inference.json file and click Create.

Step 6: Configure API Settings
- Select the new API in API Management.
- Go to Settings, then Subscription.
- Ensure Subscription required is checked and Header name is set to api-key.
- Copy the api-key to notepad as you will use many times.

Step 7: Update API Management Policy
- Download the [apim-policy.xml](https://github.com/Azure-Samples/openai-apim-lb/blob/main/apim-policy.xml)
- Edit apim-policy.xml to include all the Azure OpenAI instances you want to use and assign the desired priority to each instance. For us,
~~~
backends.Add(new JObject()
                    {
                        { "url", https://xjxfarm0.cognitiveservices.azure.com },
                        { "priority", 1},
                        { "isThrottling", false }, 
                        { "retryAfter", DateTime.MinValue } 
                    });

                    backends.Add(new JObject()
                    {
                        { "url", https://xjxfarm1.cognitiveservices.azure.com },
                        { "priority", 0},
                        { "isThrottling", false },
                        { "retryAfter", DateTime.MinValue }
                    });
~~~
- Edit apim-policy.xml to fix "APIM returns 500 Error when one of backend azure openai returns 429 at the first time. #29" by making a one-line change:
~~~
 <retry condition="@(context.Response != null && (context.Response.StatusCode == 401 || context.Response.StatusCode == 429 || context.Response.StatusCode >= 500) && (int.Parse((string)context.Variables["remainingBackends"])) > 0)" count="50" interval="0">
~~~

Step 8: Apply Policy in API Management
- Return to API Management and select Design.
- Choose All operations and click the </> icon in inbound processing.
- Replace the code with your updated apim-policy.xml.
- Save the changes.

Step 9: Finalize Subscription Settings
- Go to Subscriptions in API Management.
- Click + Add Subscription.
- Name the subscription, scope it to "Azure OpenAI Service API", and create it.
- Copy the subscription key to notepad.

Step 10: Test the Configuration
- Test the setup first from portal/APIM/API/First method/Test with setting of
~~~
deployment-id=gpt-35-turbo
api-version=2024-06-01
api-key=<your value>
request_body:
"messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Please tell me the history of United States."}
    ]
~~~
- Test the setup with the [sample code](https://github.com/Azure-Samples/openai-apim-lb/blob/main/docs/sample-code.md).
- Since this sample code didn’t tell you which instance is in use, we fall back to vanilla http call as you can see in tryme.py. With this code, we can easily see the aifarm1 hit first, and the aifarm0. As we may already reach the rate limit and need wait a few second to see another call go through, possible hit aifarm1 again.
