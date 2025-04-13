Comprehensive Developer Guide to Mistral OCR API (mistral-ocr-latest) with Python1. Introduction: Harnessing Mistral's Advanced OCRMistral AI has introduced a powerful Optical Character Recognition (OCR) API, accessible via the mistral-ocr-latest model identifier, designed to set a new benchmark in document understanding.1 This API goes beyond simple text extraction, offering capabilities to comprehend complex document elements including interleaved media (images), text structure (headers, paragraphs, lists), tables, and even mathematical equations with high accuracy.1 It accepts PDF and image files as input, returning extracted content in a structured Markdown format that preserves much of the original layout and includes references to embedded images.1Key strengths highlighted include:
State-of-the-Art Understanding: Excels with intricate layouts, mathematical expressions (like LaTeX), tables, and figures often found in scientific papers or technical documents.1
Multilingual & Multimodal: Natively handles thousands of scripts, fonts, and languages without explicit configuration, and uniquely extracts embedded images alongside text.1 Benchmarks suggest superior performance compared to competitors like Google Document AI and Azure OCR across various document types, including multilingual and scanned documents.1
Speed & Scalability: Processes documents rapidly, reportedly up to 2000 pages per minute on a single node, suitable for high-throughput environments.1
Structured Output: Returns content primarily in Markdown, facilitating easy parsing and integration into downstream applications.2 JSON output is also mentioned as possible, particularly for structured extraction use cases.1
Document Understanding: Combines OCR with Mistral's large language models (LLMs) to enable natural language querying, summarization, and information extraction directly from document content.2
This guide focuses on empowering Python developers to leverage the mistral-ocr-latest API effectively. It details the setup, core API usage for single documents (PDFs, images via URL or upload), advanced features like handling embedded images and combining OCR with chat models, and critically, explores batch processing as a means to significantly reduce costs for large-scale document processing tasks.1 We will also delve into community-reported issues and troubleshooting strategies to navigate potential challenges.2. Setup and AuthenticationBefore interacting with the Mistral OCR API, developers need to set up an account, obtain an API key, and install the necessary Python client library.Account and API Key:
Create Account: Sign up or log in to the Mistral AI platform at console.mistral.ai.11
Activate Billing: Navigate to "Workspace" -> "Billing" to add payment information. Activating payments is necessary to enable API key usage.11
Generate API Key: Go to the "API keys" page and click "Create new key". Provide an optional name and expiry date for organizational purposes.8
Secure Key: Immediately copy the generated API key and store it securely. Mistral emphasizes not sharing this key.11 A common practice is to store the key as an environment variable (e.g., MISTRAL_API_KEY).
Python Client Installation:Mistral provides an official Python client library (mistralai) for seamless API interaction.8 Install it using pip:Bashpip install mistralai
For managing environment variables (like the API key stored in a .env file), the python-dotenv package is recommended. The datauri package can also be useful for handling base64 image data.3Bashpip install python-dotenv datauri
Initializing the Client:Instantiate the Mistral client in your Python script, typically loading the API key from environment variables:Pythonimport os
from mistralai import Mistral
from dotenv import load_dotenv

# Load environment variables from.env file (optional, requires python-dotenv)
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable not set.")

# Initialize the Mistral client
client = Mistral(api_key=api_key)

print("Mistral client initialized successfully.")
While this guide focuses on Python, the official Mistral documentation also provides examples using TypeScript and curl for interacting with their APIs.113. Core OCR Functionality: client.ocr.processThe primary method for performing OCR tasks using the Mistral Python client is client.ocr.process. This function handles sending the document (via URL, upload, or image data) to the API and returning the processed results.2 An asynchronous version, client.ocr.process_async, is also available for non-blocking operations 14, but this guide will focus on the synchronous client.ocr.process for clarity.Making Single OCR Requests:The API supports processing documents provided in several ways:

Processing via Document URL (PDF):This is often the most straightforward method if the PDF document is publicly accessible online.8 The request involves specifying the model (mistral-ocr-latest) and providing a dictionary for the document parameter with type set to "document_url" and the URL itself in document_url.2
Pythonimport os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

pdf_url = "https://arxiv.org/pdf/2201.04234" # Example public PDF [2]

try:
    print(f"Processing PDF from URL: {pdf_url}")
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": pdf_url
        },
        # Optional: include_image_base64=True # To retrieve embedded images [2]
    )
    print("OCR processing successful.")
    # Process ocr_response further (see 'Understanding the Response' section)
    # print(ocr_response.pages.markdown[:500]) # Example: Print first 500 chars of page 1

except Exception as e:
    print(f"An error occurred during OCR processing: {e}")




Processing Local Files (PDF Upload):To process a PDF file stored locally, a two-step workflow is required as the API needs a URL to access the content 2:

Upload: Use client.files.upload to send the local file to Mistral's temporary storage. It is critical to specify purpose="ocr" in this call. This parameter appears essential for the OCR workflow, likely informing the backend how to handle the file and apply necessary validations, differentiating it from uploads for other purposes like batch jobs (purpose="batch") or fine-tuning.2 The upload returns a file object containing a unique id.
Get Signed URL: Use client.files.get_signed_url with the file_id obtained from the upload step. This generates a short-lived, secure URL that the OCR service can use to access the uploaded file. Specify an expiry time in seconds (e.g., 60 for one minute).2
Process OCR: Call client.ocr.process using the generated signed_url in the document_url field, setting the type to "document_url", just like the public URL method.2

Pythonimport os
from mistralai import Mistral
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

local_pdf_path = Path("uploaded_file.pdf") # Path to your local PDF file [2]

if not local_pdf_path.is_file():
    raise FileNotFoundError(f"Local PDF file not found: {local_pdf_path}")

try:
    # 1. Upload the local file
    print(f"Uploading local file: {local_pdf_path.name}")
    with open(local_pdf_path, "rb") as f:
        uploaded_file = client.files.upload(
            file={"file_name": local_pdf_path.name, "content": f},
            purpose="ocr" # Crucial for OCR workflow [2, 15, 17, 18]
        )
    print(f"File uploaded successfully. File ID: {uploaded_file.id}")

    # 2. Get a temporary signed URL for the uploaded file
    print("Generating signed URL...")
    signed_url_response = client.files.get_signed_url(file_id=uploaded_file.id, expiry=60) # URL valid for 60 seconds
    signed_url = signed_url_response.url
    print(f"Signed URL generated: {signed_url[:50]}...") # Print partial URL for confirmation

    # 3. Process OCR using the signed URL
    print("Processing OCR using signed URL...")
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url", # Type remains 'document_url'
            "document_url": signed_url
        },
        # Optional: include_image_base64=True
    )
    print("OCR processing successful.")
    # Process ocr_response further
    # print(ocr_response.pages.markdown[:500])

except Exception as e:
    print(f"An error occurred: {e}")




Processing Images (URL or Base64):Images can be processed directly from a public URL or by sending the image data encoded in Base64 format within a data URI.2 In both cases, the document parameter's type should be "image_url".


Image URL: Provide the direct URL to the image file.
Python# (Initialize client as shown previously)

image_url = "https://raw.githubusercontent.com/mistralai/cookbook/refs/heads/main/mistral/ocr/receipt.png" # Example image URL [2, 9]

try:
    print(f"Processing image from URL: {image_url}")
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": image_url
        }
    )
    print("OCR processing successful.")
    # Process ocr_response (likely has only one page)
    # print(ocr_response.pages.markdown)

except Exception as e:
    print(f"An error occurred: {e}")



Base64 Encoded Image: Read a local image file, encode its content into Base64, and construct a data URI string (e.g., data:image/png;base64,<encoded_string>). Pass this data URI as the image_url.2
Pythonimport base64
from pathlib import Path
# (Initialize client as shown previously)

local_image_path = Path("receipt.png") # Path to your local image file [16]
mime_type = "image/png" # Adjust based on your image type (e.g., image/jpeg)

if not local_image_path.is_file():
    raise FileNotFoundError(f"Local image file not found: {local_image_path}")

try:
    # Encode the local image file to Base64
    print(f"Encoding local image: {local_image_path.name}")
    with open(local_image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URI
    data_uri = f"data:{mime_type};base64,{encoded_string}"
    print(f"Data URI created (first 60 chars): {data_uri[:60]}...")

    # Process OCR using the data URI
    print("Processing OCR using data URI...")
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url", # Type remains 'image_url'
            "image_url": data_uri
        }
    )
    print("OCR processing successful.")
    # Process ocr_response
    # print(ocr_response.pages.markdown)

except Exception as e:
    print(f"An error occurred: {e}")




Request Parameters Deep Dive:The client.ocr.process method accepts several parameters to control the OCR process. Understanding these is key to optimizing performance and output.2ParameterTypeRequiredDescription & NotesmodelstrYesSpecifies the OCR model. Use "mistral-ocr-latest".documentdictYesObject detailing the input. Must have type ("document_url" or "image_url") and the corresponding URL (document_url or image_url).pagesList[int] / NoneNoList of 0-indexed page numbers or ranges to process (e.g., ``). Processes all pages if omitted. Note potential indexing mismatch in response (see below).include_image_base64bool / NoneNoIf True, includes base64 encoded strings for images found within the document in the response. Defaults to False.image_limitint / NoneNoMaximum number of images to extract per page.image_min_sizeint / NoneNoMinimum height and width (in pixels) for an image to be extracted. Useful for ignoring small icons or noise.idstr / NoneNoOptional identifier for the request. Purpose not explicitly detailed.retriesRetryConfig/NoneNoCustom retry configuration (from mistralai.models.utils). Overrides default client retry behavior for this specific call.Table references: 2Understanding the Response:The API returns a JSON object upon successful processing, which the Python client parses into an OCRResponse object.5 The primary structure includes 2:
pages: A list where each item represents a processed page of the document.
Each page object contains:

index: The page number. Note: While the pages request parameter uses 0-based indexing 13, the example response in the documentation shows the first page having "index": 1.2 Developers should verify the actual indexing (0-based or 1-based) in the response through testing.
markdown: A string containing the extracted content of the page in Markdown format. This format preserves structural elements like headings, lists, paragraphs, and table structures recognized by the model.2
images: A list of objects representing images detected on the page. Each image object typically includes coordinates (e.g., top_left_x, top_left_y, etc.) and an identifier (id). If include_image_base64 was set to True in the request, each image object will also contain an image_base64 field with the base64 encoded image data.2 The Markdown content references these images using syntax like ![img-0.jpeg](img-0.jpeg).8
dimensions: An object providing the page's height and width in pixels, and the resolution (dpi).2


Here's how to access the Markdown content from the response:Python# Assuming ocr_response is the result from client.ocr.process
# and the call was successful

if hasattr(ocr_response, 'pages') and ocr_response.pages:
    all_markdown_content = ""
    print(f"Document processed with {len(ocr_response.pages)} pages.")

    for page in ocr_response.pages:
        # Determine page number based on observed indexing (likely 1-based from example)
        page_number = page.index
        print(f"--- Processing Page {page_number} ---")
        print(f"Dimensions: {page.dimensions.width}x{page.dimensions.height} @ {page.dimensions.dpi} DPI")
        print(f"Markdown Content (first 500 chars): \n{page.markdown[:500]}...\n")
        all_markdown_content += f"# Page {page_number}\n\n" + page.markdown + "\n\n"

    # Optionally save the combined markdown to a file
    output_md_file = "extracted_content.md"
    try:
        with open(output_md_file, "w", encoding="utf-8") as f:
            f.write(all_markdown_content)
        print(f"Combined markdown saved to {output_md_file}")
    except Exception as e:
        print(f"Error saving markdown file: {e}")
else:
    print("OCR response did not contain any pages.")

4. Batch Processing for Cost EfficiencyA significant advantage advertised for the Mistral OCR API is the potential for substantial cost savings through batch processing. Multiple sources indicate that using batch inference can effectively double the number of pages processed per dollar, representing a 50% discount compared to individual API calls.1 This makes batching highly attractive for developers dealing with large volumes of documents where immediate latency is not the primary concern.31However, the precise mechanism for achieving this batch processing discount for OCR specifically requires careful attention, as the documentation presents some ambiguity.Using the Standard Mistral Batch API (/v1/batch/jobs)Mistral offers a general-purpose Batch API endpoint (/v1/batch/jobs) designed for asynchronous processing of multiple requests.19 The workflow involves submitting a file containing multiple individual API call definitions, initiating a batch job, waiting for the job to complete, and then downloading the results.19

Input Data Format (.jsonl):The Batch API requires input data in the JSON Lines (.jsonl) format. Each line in this file must be a valid JSON object representing a single API request to be executed within the batch.19 Each JSON object (line) must include:

custom_id: A unique string identifier chosen by the developer to track this specific request within the batch job.
method: The HTTP method for the individual request (e.g., "POST").
url: The relative API endpoint path for the individual request (e.g., /v1/chat/completions).
body: The JSON payload that would normally be sent in the body of the individual API request.

For a hypothetical batch OCR job, the .jsonl file might look like this (Note: See Important Note below regarding endpoint validity):
Code snippet{"custom_id": "doc_ocr_001", "method": "POST", "url": "/v1/ocr", "body": {"model": "mistral-ocr-latest", "document": {"type": "document_url", "document_url": "https://example.com/document1.pdf"}}}
{"custom_id": "doc_ocr_002", "method": "POST", "url": "/v1/ocr", "body": {"model": "mistral-ocr-latest", "document": {"type": "document_url", "document_url": "https://example.com/document2.pdf"}, "pages": }}
{"custom_id": "img_ocr_001", "method": "POST", "url": "/v1/ocr", "body": {"model": "mistral-ocr-latest", "document": {"type": "image_url", "image_url": "https://example.com/image1.png"}, "include_image_base64": true}}



Workflow & Python Code Examples:


Prepare & Upload Input File: Create the .jsonl file containing all the individual OCR requests. Then, upload this file using client.files.upload, ensuring the purpose parameter is set to "batch".19
Pythonfrom pathlib import Path
import json
import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

# Example list of request bodies for OCR (replace with your actual data)
batch_requests =},
    {"model": "mistral-ocr-latest", "document": {"type": "image_url", "image_url": "URL_TO_IMAGE_1"}}
]

batch_input_filename = "ocr_batch_input.jsonl"
try:
    with open(batch_input_filename, "w", encoding="utf-8") as f:
        for i, req_body in enumerate(batch_requests):
            job_line = {
                "custom_id": f"ocr_job_{i+1}",
                "method": "POST",
                "url": "/v1/ocr", # *** See note below on endpoint support ***
                "body": req_body
            }
            f.write(json.dumps(job_line) + "\n")
    print(f"Batch input file '{batch_input_filename}' created.")

    # Upload the batch input file
    batch_input_path = Path(batch_input_filename)
    with open(batch_input_path, "rb") as f:
        batch_file_response = client.files.upload(
            file={"file_name": batch_input_path.name, "content": f},
            purpose="batch" # Must be 'batch' for this API [19]
        )
    batch_input_file_id = batch_file_response.id
    print(f"Batch input file uploaded successfully. File ID: {batch_input_file_id}")

except Exception as e:
    print(f"Error preparing or uploading batch input file: {e}")
    batch_input_file_id = None



Create Batch Job: Initiate the batch job using client.batch.jobs.create. Provide the input_files (a list containing the uploaded file ID), the target model (presumably mistral-ocr-latest), and the endpoint for the individual requests (e.g., /v1/ocr).19 Optional parameters include metadata for tagging the job and timeout_hours (default 24h, max 7 days).19
Pythonbatch_job_id = None
if batch_input_file_id:
    # *** IMPORTANT CAVEAT: '/v1/ocr' is NOT officially listed as a supported endpoint
    # in the main batch documentation.[19] This code assumes it *might*
    # work or requires confirmation from up-to-date official sources. ***
    target_endpoint = "/v1/ocr"
    target_model = "mistral-ocr-latest"

    print(f"Attempting to create batch job for endpoint '{target_endpoint}' and model '{target_model}'...")
    try:
        created_job = client.batch.jobs.create(
            input_files=[batch_input_file_id],
            model=target_model,
            endpoint=target_endpoint, # Critical parameter - check if valid for OCR
            metadata={"job_description": "Bulk document OCR processing"}, # Optional [19]
            # timeout_hours=12 # Optional, default 24h, max 168h (7 days) [19]
        )
        batch_job_id = created_job.id
        print(f"Batch job created successfully. Job ID: {batch_job_id}, Status: {created_job.status}")
    except Exception as e:
        # This exception might occur if the endpoint is genuinely unsupported
        print(f"Error creating batch job (Endpoint '{target_endpoint}' might be unsupported by the batch API): {e}")



Check Job Status: Batch jobs run asynchronously. Periodically poll the job status using client.batch.jobs.get(job_id=batch_job_id). The job status will transition through states like QUEUED, RUNNING, and finally settle on SUCCESS, FAILED, TIMEOUT_EXCEEDED, or CANCELLED.19 Implement a loop with a reasonable delay (e.g., 30-60 seconds) between checks.
Pythonimport time

if batch_job_id:
    print(f"Polling status for job ID: {batch_job_id}")
    while True:
        try:
            retrieved_job = client.batch.jobs.get(job_id=batch_job_id)
            current_status = retrieved_job.status
            print(f" Job Status: {current_status}")

            if current_status in:
                print(f"Job {batch_job_id} finished with final status: {current_status}")
                break

            # Wait before the next poll
            time.sleep(30) # Check every 30 seconds

        except Exception as e:
            print(f"Error retrieving job status: {e}")
            # Implement retry logic or break if error persists
            time.sleep(60) # Wait longer after an error



Download Results: If the final job status is SUCCESS, the retrieved_job object will contain an output_file ID. Use client.files.download(file_id=output_file_id) to retrieve the results file.19 This output file is also in .jsonl format, where each line corresponds to the result of an individual request identified by its custom_id. If the job fails, an error_file ID might be present instead.
Pythonif batch_job_id and retrieved_job.status == "SUCCESS":
    output_file_id = retrieved_job.output_file
    if output_file_id:
        print(f"Job succeeded. Downloading results file: {output_file_id}")
        try:
            output_file_stream = client.files.download(file_id=output_file_id)

            # Save the results file
            output_filename = f"batch_results_{batch_job_id}.jsonl"
            with open(output_filename, "wb") as f:
                for chunk in output_file_stream.iter_bytes():
                    f.write(chunk)
            print(f"Batch results saved to {output_filename}")

            # Example: Process the downloaded results file
            print("\nProcessing results...")
            successful_requests = 0
            failed_requests = 0
            with open(output_filename, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        result_data = json.loads(line)
                        custom_id = result_data.get("custom_id")
                        response_status = result_data.get("response", {}).get("status_code")
                        if response_status == 200:
                            successful_requests += 1
                            # Access the actual OCR response content:
                            # ocr_result_body = result_data.get("response", {}).get("body", {})
                            # print(f"Success for {custom_id}: {ocr_result_body}")
                        else:
                            failed_requests += 1
                            error_body = result_data.get("response", {}).get("body", {})
                            print(f"Failed request {custom_id}: Status {response_status}, Error: {error_body}")
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode line: {line.strip()}")
                    except Exception as e:
                        print(f"Error processing result line: {e}")
            print(f"\nResult Summary: {successful_requests} successful, {failed_requests} failed.")

        except Exception as e:
            print(f"Error downloading or processing results file: {e}")
    else:
        print("Job succeeded but no output file ID was found.")

elif batch_job_id:
    print(f"Job {batch_job_id} did not succeed (Status: {retrieved_job.status}).")
    error_file_id = retrieved_job.error_file
    if error_file_id:
        print(f"Error file ID: {error_file_id}. Consider downloading it for details.")
        # Optionally download and inspect the error file similar to the output file
    else:
        print("No error file ID provided.")





Important Note on Batch OCR Endpoint Support:There is significant ambiguity regarding whether the standard Batch API (/v1/batch/jobs) actually supports the OCR endpoint (/v1/ocr).

The primary Batch API documentation 19 explicitly lists the supported endpoints: /v1/embeddings, /v1/chat/completions, /v1/fim/completions, /v1/moderations, and /v1/chat/moderations. Crucially, /v1/ocr is absent from this list.
The main API reference 23 also lists the /v1/ocr endpoint separately from the /v1/batch endpoints.
However, multiple official announcements and third-party articles explicitly mention a 50% cost discount for "batch inference" or "batch OCR".1
Furthermore, Mistral maintains official "Cookbooks," including one titled "Batch OCR".2 Unfortunately, the provided research snippets do not contain the specific code from this cookbook that demonstrates how batch OCR is invoked.22 Snippet 22 references the cookbook and mentions batch inference but cuts off before the implementation. Snippet 30 mentions batching for OCR returning results within 24 hours, consistent with the general batch API behavior. Some community members have reported trying batch OCR without success, specifically encountering the image placeholder issue.27

This discrepancy creates uncertainty. It is possible that:a)  The /v1/ocr endpoint is supported by the standard /v1/batch/jobs API, but the documentation 19 is lagging or incomplete.b)  There is a different, perhaps undocumented or less prominent, mechanism or specific endpoint dedicated to batch OCR.c)  The term "batch discount" might refer simply to the efficiency gain of processing a multi-page PDF in a single /v1/ocr call, although the explicit 50% figure tied to "batch inference" makes this less likely.


Guidance for Developers:Given this uncertainty, developers aiming for the batch processing discount for OCR must verify the correct implementation method.

Consult Latest Official Documentation: Check the most up-to-date Mistral API documentation on their official website (https://docs.mistral.ai/) 34 and the specific content of the "Batch OCR" cookbook within their GitHub repository (https://github.com/mistralai/cookbook).2 Look for explicit examples using client.batch.jobs.create with the /v1/ocr endpoint or any alternative batch OCR methods.
Contact Mistral Support: If the documentation remains unclear, contacting Mistral support directly via La Plateforme is the most reliable way to get confirmation.35
Experiment Cautiously: If attempting to use the standard /v1/batch/jobs endpoint with /v1/ocr, start with small test batches and monitor results closely, being prepared for potential errors or unexpected behavior.
Alternative Strategy (Parallel Processing): If true batching for OCR proves infeasible or undocumented, developers can simulate batching by running multiple individual client.ocr.process calls concurrently (e.g., using Python's asyncio or concurrent.futures). This approach does not provide the batch discount but can improve throughput. However, it requires careful management to stay within the workspace's rate limits (Requests Per Second and Tokens Per Minute).35


5. Advanced Features and TechniquesBeyond basic text extraction, the Mistral OCR API and its ecosystem offer advanced capabilities, particularly when combined with other Mistral models.Document Understanding: Combining OCR with Chat ModelsA powerful pattern involves using the structured Markdown output from client.ocr.process as rich context for subsequent calls to Mistral's chat completion models (like mistral-small-latest or mistral-large-latest). This enables sophisticated document interaction tasks such as question answering, summarization, or extracting specific data points into structured formats like JSON.1Mistral provides cookbooks demonstrating this, such as "Tool Use and Document Understanding" and "Structured OCR".2 The general workflow is:
Perform OCR on the document using client.ocr.process.
Extract the Markdown content from the relevant pages of the ocr_response.
Construct a prompt for client.chat.complete. This prompt should include the extracted Markdown text (potentially truncated to fit context limits) and clear instructions for the desired task (e.g., "Extract the author names and publication year from the following research paper abstract: {ocr_markdown}").
Call client.chat.complete with the constructed prompt and process the response.
Pythonimport os
import json
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

# --- Assume ocr_response is obtained from a previous client.ocr.process call ---
# Example: Combine markdown from all pages
try:
    if hasattr(ocr_response, 'pages') and ocr_response.pages:
        ocr_markdown = "\n\n".join([page.markdown for page in ocr_response.pages])
        print(f"Combined markdown length: {len(ocr_markdown)} characters.")
    else:
        print("No pages found in OCR response.")
        ocr_markdown = ""

    if ocr_markdown:
        # --- Use a chat model for structured extraction ---
        chat_model = "mistral-small-latest" # Or mistral-large-latest, etc. [2, 9]
        max_context_chars = 16000 # Example limit, adjust based on model and needs

        extraction_prompt = f"""
        Based on the document content provided below, extract the following information
        into a valid JSON object:
        - "title": The main title of the document.
        - "authors": A list of author names.
        - "abstract_summary": A concise one-sentence summary of the abstract, if present.
        - "key_findings": A list of 2-3 main findings or conclusions mentioned.

        If any information is not found, use null as the value.

        Document Content:
        ---
        {ocr_markdown[:max_context_chars]}
        ---

        JSON Output:
        """

        messages = [{"role": "user", "content": extraction_prompt}]

        print(f"\nSending request to chat model '{chat_model}' for structured extraction...")

        # Consider using JSON mode if supported and needed for reliability
        # response_format = {"type": "json_object"}
        # chat_response = client.chat.complete(
        #     model=chat_model,
        #     messages=messages,
        #     response_format=response_format
        # )

        # Standard chat completion call
        chat_response = client.chat.complete(
            model=chat_model,
            messages=messages
        )

        extracted_data_str = chat_response.choices.message.content
        print("\nRaw response from chat model:")
        print(extracted_data_str)

        # Attempt to parse the response as JSON
        try:
            # Clean potential markdown code fences
            if extracted_data_str.strip().startswith("```json"):
                 extracted_data_str = extracted_data_str.strip()[7:-3].strip()
            elif extracted_data_str.strip().startswith("```"):
                 extracted_data_str = extracted_data_str.strip()[3:-3].strip()

            extracted_json = json.loads(extracted_data_str)
            print("\nSuccessfully parsed JSON:")
            print(json.dumps(extracted_json, indent=2))
        except json.JSONDecodeError as json_err:
            print(f"\nCould not parse response as JSON: {json_err}")
        except Exception as parse_err:
            print(f"\nAn error occurred during JSON parsing: {parse_err}")

except NameError:
     print("Error: 'ocr_response' not defined. Ensure OCR was run first.")
except Exception as e:
    print(f"An error occurred in the document understanding step: {e}")

An alternative, potentially simpler approach for some use cases is Mistral's built-in document understanding feature within the chat completion API itself. Instead of performing OCR separately, the document URL can be included directly as part of the message content using a specific structure ({"type": "document_url", "document_url": "..."}).2 The API presumably handles the OCR implicitly in this case. While this simplifies the initial request, it offers less direct control over the OCR parameters and output compared to the two-step ocr.process followed by chat.complete method.Handling Embedded Images (include_image_base64)To retrieve the actual image data alongside the text, set the include_image_base64=True parameter when calling client.ocr.process.2When this flag is enabled, the images list within each page object in the response will contain objects that include an image_base64 field holding the base64-encoded string of the image data.2 The corresponding Markdown text will still reference the image using relative paths like ![img-0.jpeg](img-0.jpeg).8To use these images, developers need to decode the base64 string and save the image data to a file. It's often practical to name the saved file according to the reference used in the Markdown (e.g., img-0.jpeg) so that rendering the Markdown displays the images correctly.Pythonimport base64
from pathlib import Path
import re

# --- Assume ocr_response is from client.ocr.process with include_image_base64=True ---

output_image_dir = Path("./extracted_images")
output_image_dir.mkdir(exist_ok=True)
print(f"Saving extracted images to: {output_image_dir.resolve()}")

image_save_count = 0
image_error_count = 0

try:
    if hasattr(ocr_response, 'pages') and ocr_response.pages:
        for page in ocr_response.pages:
            page_number = page.index # Assuming 1-based index from example [2]
            if hasattr(page, 'images') and page.images:
                for img in page.images:
                    if hasattr(img, 'image_base64') and img.image_base64:
                        try:
                            # Attempt to find image reference in markdown to get filename
                            # Example pattern:![alt text](filename.ext)
                            # This assumes img.id might correspond to the number in 'img-N.jpeg'
                            img_filename = f"img-{img.id}.jpeg" # Default guess
                            pattern = rf"!\[.*?\]\((img-{img.id}\.(?:jpeg|jpg|png|gif))\)"
                            match = re.search(pattern, page.markdown)
                            if match:
                                img_filename = match.group(1)
                            else:
                                # Fallback if pattern doesn't match or id is different
                                print(f"Warning: Could not find markdown reference for image ID {img.id} on page {page_number}. Using default filename.")
                                # Use a unique name based on page and id
                                img_filename = f"page_{page_number}_img_{img.id}.jpg" # Default extension

                            img_path = output_image_dir / img_filename
                            img_data = base64.b64decode(img.image_base64)

                            with open(img_path, "wb") as f:
                                f.write(img_data)
                            # print(f"Saved image: {img_path}")
                            image_save_count += 1

                        except base64.binascii.Error as b64_err:
                            print(f"Error decoding base64 for image ID {getattr(img, 'id', 'N/A')} on page {page_number}: {b64_err}")
                            image_error_count += 1
                        except Exception as e:
                            print(f"Error processing/saving image ID {getattr(img, 'id', 'N/A')} on page {page_number}: {e}")
                            image_error_count += 1
        print(f"\nImage extraction complete. Saved: {image_save_count}, Errors: {image_error_count}")
    else:
        print("No pages found in OCR response or include_image_base64 was likely False.")

except NameError:
     print("Error: 'ocr_response' not defined. Ensure OCR was run first with include_image_base64=True.")
except Exception as e:
     print(f"An unexpected error occurred during image handling: {e}")
Page Selection and Image FilteringFor large documents or specific use cases, developers can refine the OCR process using request parameters:
pages: Process only a subset of pages by providing a list of 0-indexed page numbers or ranges (e.g., pages=, pages=["0-2", "5"]). This can significantly reduce processing time and cost for large PDFs where only certain sections are relevant.13
image_limit: Control the maximum number of embedded images extracted per page. This is useful if images are numerous but not all are needed, helping to manage response size.13
image_min_size: Set a threshold for the minimum height and width (in pixels) of images to be extracted. This allows filtering out small, potentially irrelevant images like icons or logos.13
6. Pricing and Cost OptimizationUnderstanding the cost structure is crucial for effectively utilizing the Mistral OCR API, especially at scale.mistral-ocr-latest Pricing Details:The pricing for the mistral-ocr-latest model is based on the number of pages processed. While official pricing pages should always be consulted for the latest figures 38, available information suggests the following structure 1:FeatureUnitPrice (USD, Approx.)NotesStandard OCRPage~$0.001Equivalent to $1 per 1,000 pages.Batch OCRPage~$0.0005Equivalent to $1 per 2,000 pages (Advertised 50% discount). Realization depends on correctly implementing batch OCR (see Sec 4).File Size LimitFileN/AMaximum 50 MB per file processed in a single API call.Page Count LimitFileN/AMaximum 1,000 pages per file processed in a single API call.Table references: 1It is essential to verify these rates on the official Mistral AI pricing page or within the La Plateforme console, as pricing can change.38 Note that snippet 39 initially found the pricing page unhelpful, highlighting the need to check the current official source.Batch Processing Discount:The most significant cost optimization strategy offered is the batch processing discount. As noted, this promises roughly a 50% reduction in cost per page.1 However, as detailed in Section 4, the exact method for invoking batch OCR and guaranteeing this discount requires clarification from official Mistral resources due to documentation ambiguities.Best Practices for Cost Minimization:Beyond batching, developers can employ several strategies to manage OCR costs:
Use Batching (If/When Feasible): Once the implementation details are confirmed, prioritize using the batch API for high-volume, non-urgent OCR tasks to leverage the potential 50% discount.
Process Only Necessary Pages: For large multi-page documents (PDFs), use the pages parameter in client.ocr.process to specify only the required pages or page ranges, avoiding unnecessary processing costs.13
Optimize Input Quality: Pre-processing documents to improve clarity (e.g., deskewing scanned pages, enhancing contrast on faded text) can potentially increase OCR accuracy.3 Better accuracy reduces the likelihood of needing costly re-processing or extensive manual correction/validation downstream.
Implement Application-Level Caching: If your application might request OCR for the same document multiple times, implement a caching layer (e.g., storing results based on a document hash or identifier) to avoid redundant API calls.
Monitor Usage and Set Limits: Regularly check API consumption and associated costs through the Mistral La Plateforme dashboard and billing section.11 Configure spend limits within your workspace, but be aware that high-throughput batch jobs might slightly exceed these limits before processing stops.19
7. Community Insights & TroubleshootingLeveraging community feedback from forums like Stack Overflow ([mistral-ai] tag) 40 and Reddit (r/MistralAI) 28 can provide valuable insights into common challenges and potential workarounds when using the mistral-ocr-latest API.Common Issues & Bugs Reported by the Community:
Issue 1: Image Placeholder Output (![img-N.jpeg]): This appears to be the most frequently encountered problem. Users report that for certain inputs, particularly PDFs composed entirely of scanned images, receipts, bank cheques, or even some standard image files, the API returns Markdown containing only image references (e.g., ![img-0.jpeg](img-0.jpeg)) instead of the expected extracted text.14 This behavior seems inconsistent and sometimes occurs randomly 28, directly contradicting the API's advertised capability to handle complex visual layouts. Some benchmarks suggest this "overzealous image extraction" significantly impacts accuracy on certain document types like receipts.43
Issue 2: Limited Success with Non-Searchable PDFs: Corroborating the first issue, some developers found that text extraction only worked reliably if the input PDF already contained selectable/searchable text layers. Scanned, image-only PDFs often resulted in the image placeholder output.27
Issue 3: Multi-Page Image Input Limitation: A specific report indicated that when a single image file containing photographs of multiple document pages was submitted, the API only processed the content from the first visible page, ignoring the others.41 This might be an inherent limitation or related to the per-page pricing model.
Issue 4: Accuracy Concerns & Hallucinations: While benchmarks show strong performance overall 1, some users have noted specific accuracy failures (e.g., misinterpreting similar digits like 5, 6, 8 on scanned documents 44) or expressed concerns about the inherent risk of hallucinations (generating plausible but incorrect text) common to LLM-based approaches.43 Community-run benchmarks also show variability in performance depending on the document type and metric used.43
Issue 5: API Key / Authentication Errors (401): As with any API, standard 401 Unauthorized errors can occur. Common causes include using an incorrect API key, forgetting to activate billing on the Mistral account (which enables the key), or errors in how the authentication header is passed (though the official Python client handles this automatically if initialized correctly).11
Issue 6: SDK/Dependency Issues: Less frequently, users might encounter Python environment issues, such as installation problems, dependency conflicts (e.g., potential clashes with specific versions of libraries like Pydantic mentioned in a GitHub issue 20), or bugs within the client library itself.20
Workarounds and Solutions:The following table summarizes potential solutions and workarounds based on documentation and community discussions:
IssuePotential Solution / WorkaroundRelevant SnippetsImage Placeholder Output (![img-N.jpeg])1.  Verify Input: Ensure the document isn't entirely blank or corrupted. <br> 2.  Try Chat Completion + Document URL: Use client.chat.complete passing the document URL directly in the message content (type: "document_url"). Some users found this yielded better text extraction for problematic files.42 <br> 3.  Alternative OCR Tools: If Mistral consistently fails for specific critical document types (e.g., scanned receipts, cheques), consider evaluating alternative libraries (marker-pdf 27) or cloud services (Google Document AI, Azure AI Vision 1). <br> 4.  Pre-process Input: For scanned documents, try improving image quality (deskew, increase contrast, ensure >300 DPI) before sending to the API.3 If possible, convert image-only PDFs to searchable PDFs using external tools first. <br> 5.  Check include_image_base64: While setting this to True retrieves the image itself, it doesn't force text extraction if the model fails to recognize text.27 <br> 6.  Contact Mistral Support: Persistent issues might indicate an underlying bug worth reporting.14Only First Page Processed (Multi-page Image)Split Image: Manually pre-process the single image file to separate it into individual images, one per page. Submit each page image as a separate API request.41Accuracy Issues / Hallucinations1.  Optimize Input Quality: Provide the clearest, highest-resolution input possible.3 <br> 2.  Post-processing/Validation: Use a reliable chat model (e.g., mistral-large-latest) to review, correct, or reformat the OCR output based on specific rules or prompts. Implement domain-specific validation checks on extracted data. <br> 3.  Cross-Reference (Costly): For extremely critical data, consider processing with multiple OCR services and comparing/reconciling the results.43 <br> 4.  Note on Fine-tuning: Mistral supports fine-tuning for its chat models, but not currently for the mistral-ocr-latest model itself.7 Fine-tuning a chat model could help improve post-processing of OCR output.43401 Unauthorized Error1.  Verify API Key: Double-check the key string is correct and hasn't expired or been revoked. <br> 2.  Confirm Billing Activation: Ensure payment details are added and active in the Mistral Workspace Billing section.11 <br> 3.  Check Client Initialization: Ensure the Mistral(api_key=...) client is initialized correctly with the valid key.11Rate Limit Errors (429)1.  Implement Retries: Use exponential backoff logic. The mistralai client has built-in retries, but check its behavior for 429s or use the retries parameter for custom configuration.13 Be aware that wrappers (like older LangChain versions) might have had issues handling 429s correctly.47 <br> 2.  Check & Respect Limits: Monitor your workspace's specific RPS and Token/Minute limits via La Plateforme 35 and ensure your application throttles requests accordingly. <br> 3.  Batch API Note: Using the standard Batch API (if applicable for OCR) does not count differently against rate limits compared to individual calls; it primarily offers cost and potential throughput benefits.1919Timeouts1.  Increase Client Timeout: Investigate if the underlying HTTP client used by mistralai (likely httpx) allows setting longer request timeouts during client initialization. <br> 2.  Process Smaller Chunks: For extremely large or complex single documents that might exceed processing time limits, consider splitting the document (e.g., using the pages parameter for PDFs) and submitting smaller chunks in separate requests.3 <br> 3.  Batch Job Timeout: Remember that standard batch jobs have a default timeout of 24 hours, adjustable via the timeout_hours parameter (up to 7 days) upon job creation.19 Jobs exceeding this will terminate with a TIMEOUT_EXCEEDED status.3
Error Handling in Code:Robust applications should anticipate potential API errors. The mistralai client typically raises exceptions for issues. While specific exception types might evolve, common ones could include subclasses of MistralException, such as MistralAPIException (for API-returned errors like 4xx/5xx) or MistralConnectionException (for network issues).3 Snippet 13 specifically mentions models.HTTPValidationError (likely for 422 status) and models.SDKError (for general 4XX/5XX errors).Use standard Python try...except blocks to catch these exceptions around API calls:Pythontry:
    ocr_response = client.ocr.process(...)
    # Process successful response
except MistralAPIException as api_err:
    print(f"Mistral API Error: Status Code: {api_err.status_code}, Message: {api_err.message}")
    # Handle specific status codes (e.g., 401, 429, 422)
except MistralConnectionException as conn_err:
    print(f"Connection Error: {conn_err}")
    # Handle network issues, maybe retry later
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    # General fallback
Implement retry logic, especially for transient errors like 429 (Rate Limit Exceeded) or potential 5xx server errors. Leverage the client's built-in retry mechanism or the retries parameter for fine-grained control.13Rate Limits and Usage Tiers:Mistral enforces API usage limits to ensure fair use and manage capacity. These limits are applied at the workspace level and depend on the usage tier associated with the workspace.35
Types of Limits: Requests Per Second (RPS) and Tokens Per Minute/Month.
Tiers: Different tiers exist, including a free tier with restrictive limits suitable mainly for exploration, and paid tiers with higher limits appropriate for development and production.35
Checking Limits: Developers must check their current workspace-specific limits directly on La Plateforme at admin.mistral.ai/plateforme/limits.35
Limit Increases: If higher limits are required, contact Mistral support through the platform.35
Batch API Impact: Using the standard asynchronous Batch API does not affect or bypass these rate limits.19 The limits still apply to the underlying requests executed within the batch job.
8. ConclusionThe Mistral OCR API, accessed via mistral-ocr-latest, presents a compelling option for developers needing advanced document processing capabilities within their Python applications. Its strengths lie in its potential for high accuracy on complex documents containing mixed content (text, images, tables, math), native multilingual support, and the generation of structured Markdown output that preserves document layout.1 The integration pathway with Mistral's chat models for further document understanding (Q&A, summarization, structured extraction) adds significant value.2However, developers should proceed with awareness of potential challenges highlighted by community feedback. The most significant reported issue involves the API returning image placeholders instead of extracted text for certain document types, particularly scanned or image-based PDFs and receipts.27 Accuracy, while generally strong according to benchmarks, can vary, and the risk of LLM hallucinations exists.43Final Recommendations:
Test Thoroughly: Before committing to production use, rigorously test the mistral-ocr-latest API with representative samples of your specific target documents (e.g., invoices, scanned forms, technical papers) to validate accuracy and reliability, paying close attention to the image placeholder issue.
Verify Batch OCR Implementation: The advertised 50% cost saving for batch processing is highly attractive.1 However, due to the current ambiguity in documentation regarding the specific endpoint or method 19, developers must consult the latest official Mistral documentation and the "Batch OCR" cookbook 2 or contact support to confirm the correct implementation procedure before relying on this discount.
Leverage Structured Output: Utilize the Markdown output's structure. Combine client.ocr.process with client.chat.complete for sophisticated tasks like structured data extraction or document Q&A, passing the OCR Markdown as context.
Optimize Costs: Employ cost-saving strategies such as processing only necessary pages (pages parameter), optimizing input quality, implementing application-level caching, and diligently monitoring API usage.
Implement Robust Error Handling: Include try...except blocks and appropriate retry logic (especially for rate limits and transient errors) in your code.
By understanding the capabilities, acknowledging the potential issues, and following best practices for implementation and cost management, developers can effectively integrate the Mistral OCR API to build powerful document processing solutions.Further Resources:
Official Mistral AI Documentation: https://docs.mistral.ai/ 34
Mistral AI Cookbooks (GitHub): https://github.com/mistralai/cookbook (Look for OCR-related notebooks like batch_ocr.ipynb, structured_ocr.ipynb, document_understanding.ipynb) 2
Mistral AI Python Client (GitHub): https://github.com/mistralai/client-python 48
Community Forums (Unofficial):

Stack Overflow (tag: [mistral-ai]): https://stackoverflow.com/questions/tagged/mistral-ai 40
Reddit (subreddit: r/MistralAI): https://www.reddit.com/r/MistralAI/ 28


