Investigating Mistral AI's Batch OCR Functionality: Implementation, Ambiguity, and Developer Guidance1. Executive SummaryThis report investigates the functionality and documentation surrounding batch processing for Mistral AI's Optical Character Recognition (OCR) service. Significant ambiguity exists regarding the officially supported method for processing multiple documents via the Mistral API.Analysis of official documentation, including API reference materials and OpenAPI specifications, confirms that the standard Mistral Batch API endpoint (/v1/batch/jobs) does not currently support the /v1/ocr endpoint.1 The Batch API is explicitly documented to support endpoints like /v1/chat/completions and /v1/embeddings, but /v1/ocr is consistently omitted.3Despite this, Mistral AI provides an official cookbook titled batch_ocr.ipynb, suggesting a method for batch OCR exists.4 Due to limited access to the notebook's specific code implementation in the available resources 5, its exact method cannot be definitively confirmed. However, based on the Batch API's limitations and the cookbook's description contrasting a simple loop with "Batch Inference" 5, the cookbook most likely demonstrates parallel processing of synchronous /v1/ocr calls using standard Python concurrency libraries (e.g., concurrent.futures, asyncio).This discrepancy between the Batch API's documented capabilities and the existence of a "Batch OCR" cookbook, coupled with marketing materials mentioning a 50% "batch inference" discount for OCR 6, has created confusion among developers. It is plausible that the advertised discount applies to high-volume OCR processing achieved through parallel synchronous calls, rather than via the standard /v1/batch/jobs API. However, the mechanism for applying this discount remains undocumented.Developers seeking to perform batch OCR with Mistral AI should implement parallel processing of synchronous /v1/ocr API calls. This report details common challenges encountered, including potential OCR quality issues (e.g., returning image placeholders instead of text 7), API errors (e.g., rate limiting 7), and cost management uncertainties. Comprehensive troubleshooting guidance and code structure examples are provided to assist developers in building robust batch OCR workflows.2. Investigating Official Support for Batch OCRA thorough examination of Mistral AI's official documentation and API specifications is necessary to determine the supported mechanisms for batch OCR processing. This involves analyzing the Batch API (/v1/batch/jobs), the synchronous OCR API (/v1/ocr), and the OpenAPI specification.2.1. Analysis of Batch API (/v1/batch/jobs) DocumentationThe Mistral AI Batch API provides an asynchronous mechanism for processing large volumes of requests, primarily targeting text generation and embedding tasks. Key findings from its documentation include:
Supported Endpoints: The documentation consistently lists the endpoints supported by the Batch API: /v1/embeddings, /v1/chat/completions, /v1/fim/completions, /v1/moderations, and /v1/chat/moderations.1
Omission of /v1/ocr: Across multiple official sources, including the primary Batch API capability page and the API reference, the /v1/ocr endpoint is notably absent from the list of supported endpoints.1 This strongly indicates that the standard batch processing workflow is not designed or enabled for OCR tasks.
Input Format: The Batch API requires input data to be prepared in a .jsonl file, where each line represents a single API request.3 This file is uploaded separately, and its ID is referenced when creating the batch job using methods like client.batch.jobs.create.14
Request Structure: Each line in the input .jsonl file must contain a custom_id and a body object corresponding to the parameters of the target synchronous endpoint.3 While structures are implicitly defined for supported endpoints like chat completions, no corresponding structure is documented for formatting an OCR request within this .jsonl context.3
The consistent exclusion of /v1/ocr from the Batch API's supported endpoints list is unlikely to be an oversight. It suggests a fundamental incompatibility or deliberate design choice. The Batch API appears optimized for tasks where inputs and outputs can be cleanly represented as JSON objects within the .jsonl format. OCR, however, involves handling file inputs (PDFs, images via URLs or base64 data 11) and produces potentially complex, multi-part outputs (markdown text, embedded image data). Representing these diverse OCR inputs within the rigid line-by-line JSONL structure required by the Batch API presents significant challenges, and the lack of a documented format 3 further implies this pathway is unsupported.2.2. Analysis of OCR API (/v1/ocr) DocumentationExamining the documentation for the synchronous OCR endpoint (/v1/ocr) provides further context:
Single Document Focus: The API documentation details parameters for processing a single document per request, specified via document_url (for URLs) or image_url (for image URLs or base64 data) within the document object.11
Absence of Batch Parameters: Crucially, the documentation for the /v1/ocr endpoint itself contains no parameters indicating support for multiple documents in a single call (e.g., a documents list) or any flags related to batch processing.2
Client Library Method: The official Python client provides client.ocr.process for making single, synchronous OCR requests.17 There is no documented equivalent like client.ocr.batch_process.18
The design of the /v1/ocr endpoint, centered on single-document inputs and lacking any batch-specific parameters, aligns perfectly with the findings from the Batch API documentation. It reinforces the conclusion that the standard /v1/batch/jobs workflow is not the intended method for OCR tasks. If batching were natively supported by the /v1/ocr endpoint itself, the API documentation would likely include parameters for submitting multiple document references or a batch identifier. Its absence strongly suggests each /v1/ocr call is treated as an independent, synchronous operation.2.3. OpenAPI Specification InsightsThe OpenAPI specification provides a definitive technical definition of the API structure:
Distinct Endpoints: The specification clearly defines /v1/ocr 11 and /v1/batch/jobs 11 as separate API paths.
Batch Job Endpoint Parameter: The schema for the POST /v1/batch/jobs request body explicitly defines the endpoint parameter with an enumerated list of allowed values: /v1/chat/completions, /v1/embeddings, /v1/fim/completions, /v1/moderations, and /v1/chat/moderations.1
/v1/ocr Not Allowed: The /v1/ocr endpoint is not included in the enumeration of valid values for the endpoint parameter when creating a batch job.1
This technical specification confirms that attempting to create a batch job targeting the /v1/ocr endpoint is invalid according to the API's defined structure.2.4. Table: Batch API vs. OCR API Batch Feature ComparisonThe following table summarizes the key differences in documented batch capabilities between the standard Batch API and the synchronous OCR API:
Feature/v1/batch/jobs API/v1/ocr APIPrimary Endpoint/v1/batch/jobs/v1/ocrProcessing ModeAsynchronousSynchronousInput MethodUploaded .jsonl file ID(s)Single document object (URL/Image data/Base64)Supported Target Endpoints/v1/chat/completions, /v1/embeddings, /v1/fim/completions, /v1/moderations, /v1/chat/moderations 1N/A (Endpoint is the target)Batch Parametersinput_files, endpoint, modelNone documented 2
This comparison visually highlights the lack of built-in batch processing features within the /v1/ocr endpoint and its incompatibility with the standard /v1/batch/jobs mechanism.3. Deconstructing the batch_ocr.ipynb CookbookDespite the evidence indicating /v1/ocr is not supported by the standard Batch API, Mistral provides an official cookbook specifically for batch OCR, adding to the confusion.3.1. Cookbook Existence and PurposeThe official Mistral AI cookbook repository on GitHub includes a notebook named batch_ocr.ipynb.4 Its stated purpose is "Using OCR to extract text data from datasets" 4 or, more explicitly, "Apply OCR to Convert Images into Text" using two methods: one "Without Batch Inference" (looping) and another "With Batch Inference: Leveraging Batch Inference to extract text with a 50% cost reduction".5The existence of this official example confirms that Mistral acknowledges the need for batch OCR processing and provides some form of guidance. The naming and description, particularly the use of "Batch Inference," naturally lead developers to assume it utilizes the /v1/batch/jobs API.3.2. Analysis of the Batch Implementation MethodDirect analysis of the notebook's code is hindered by the limited content available in the provided research materials.5 However, several factors strongly suggest the "Batch Inference" method described does not use the /v1/batch/jobs API:
Batch API Incompatibility: As established in Section 2, /v1/ocr is not a supported endpoint for /v1/batch/jobs. Therefore, the cookbook cannot be using the standard Batch API for OCR.
Cookbook Description: The description explicitly contrasts the "Without Batch Inference" method (implying a simple loop) with the "With Batch Inference" method.5 This suggests the latter employs a more sophisticated technique for parallelization.
Common Practice: The standard approach for batching requests to APIs that lack native batch support is to implement client-side parallel processing, making multiple synchronous calls concurrently. Libraries like Python's concurrent.futures or asyncio are commonly used for this.32 Examples exist showing this pattern for other OCR tools like Tesseract 35 and for general API interaction.34 A blog post reviewing Mistral OCR usage even explicitly demonstrates a simple loop for "Bulk Document Processing" that could be easily parallelized.22
Cost Reduction Mention: The reference to a "50% cost reduction" 5 likely ties into Mistral's general pricing announcement for batch processing.6 While the standard Batch API offers this discount 3, it's possible Mistral applies a similar discount logic to high-volume synchronous OCR calls, or the cookbook description might be slightly inaccurate if the discount is strictly tied to the /v1/batch/jobs API. (This ambiguity is discussed further in Section 5.3).
Based on this evidence, the most logical conclusion is that the batch_ocr.ipynb cookbook demonstrates how to achieve batch-like processing for OCR by implementing parallel execution of synchronous /v1/ocr calls. The term "Batch Inference" is likely used loosely in the cookbook's description to refer to this parallel processing pattern, rather than the specific /v1/batch/jobs API endpoint.This interpretation resolves the conflict between the Batch API documentation and the cookbook's existence. However, the lack of explicit clarification in official documentation or the cookbook itself is the primary source of developer confusion. Mistral likely intended the cookbook as a practical guide to the workaround for batch OCR, but the naming and description created ambiguity.3.3. Input .jsonl Format (if applicable)Since the cookbook likely implements parallel synchronous calls, it would not utilize the .jsonl file format required by the /v1/batch/jobs API. Input data (e.g., a list of image file paths or document URLs) would be managed within the Python script using standard data structures and iterated over by the parallel processing framework.3.4. Table: batch_ocr.ipynb Implementation Summary (Inferred)Based on the available information and logical deduction, the likely implementation methods demonstrated in the batch_ocr.ipynb cookbook are summarized below:Aspect"Without Batch Inference" (Cookbook Method 1)"With Batch Inference" (Cookbook Method 2 - Inferred)Underlying MechanismSimple Python loopParallel synchronous API callsAPI Endpoint Used/v1/ocr (synchronous)/v1/ocr (synchronous, called in parallel)Input FormatList/iterable of document paths/URLsList/iterable of document paths/URLsKey Library Usedmistralaimistralai, concurrent.futures / asyncio (likely)4. Community Experiences and Alternative StrategiesDeveloper forums, GitHub issues, and blog posts provide valuable insights into real-world experiences with Mistral OCR, particularly concerning batch processing attempts and encountered errors.4.1. Reported Successes/Failures with Batch API for OCRConsistent with the documentation analysis, there are no verifiable reports in the provided materials of developers successfully using the /v1/ocr endpoint with the standard /v1/batch/jobs API. Instead, numerous reports highlight problems and confusion:
OCR Failures: Developers frequently report the /v1/ocr endpoint returning image placeholders (e.g., ![img-0.jpeg](img-0.jpeg)) instead of extracted text, especially when processing scanned PDFs, PDFs containing images, or even standalone image files.7 This issue is documented on Stack Overflow 8 and Reddit.7
Document-Specific Failures: The OCR API reportedly fails entirely on certain document types, such as bank cheques.38
Inconsistent Behavior: Some users note that while the API fails, Mistral's own Le Chat interface successfully processes the same document.7 Others found success using the chat completion API (/v1/chat/completions) with document URLs passed as context for specific data extraction, even when the dedicated /v1/ocr endpoint failed.38
Alternative Tools: Faced with these issues, some developers report switching to alternative OCR tools like marker-pdf 8 or comparing Mistral OCR unfavorably to other services for specific use cases.43
The widespread reports of errors and inconsistencies with the synchronous /v1/ocr endpoint itself, particularly regarding image handling within documents, are critical. These underlying quality issues exacerbate the challenges of implementing reliable batch processing, regardless of the method used. If the core OCR function fails intermittently or for certain document types, simply parallelizing the calls will scale the unreliability.4.2. Common Errors Encountered by DevelopersDevelopers attempting batch OCR workflows (primarily via parallel synchronous calls) or even single OCR calls have reported various errors:
Content Errors:

Returning image placeholders (![img-N.jpeg]) instead of text.7
Complete failure on specific document types (e.g., bank cheques).38
OCR quality issues: Hallucinations, missing text (headers/footers), poor table recognition, ignoring small fonts, misreading characters (e.g., 5/6/8 confusion), inconsistent results.40


API/Network Errors:

429 Too Many Requests: Rate limit exceeded due to excessive parallel calls.7
400 Bad Request: Likely due to malformed requests, potentially incorrect JSON body if attempting unsupported methods.49
401 Unauthorized: Authentication issues, possibly incorrect API key handling.50
422 Unprocessable Entity: Validation errors, potentially from incorrect parameters or attempting unsupported operations (like using /v1/ocr with /v1/batch/jobs).18
Timeout Errors: Individual OCR calls taking too long, especially for large or complex documents.9
File Upload Errors: Issues with the file upload process required for local files, e.g., Field required error.7


4.3. Community Workarounds (Parallel Processing)Given the lack of official Batch API support for /v1/ocr, the developer community has implicitly adopted parallel execution of synchronous calls as the standard workaround:
Standard Libraries: Python developers leverage built-in libraries like concurrent.futures (using ThreadPoolExecutor for I/O-bound tasks like API calls) or asyncio for managing concurrent requests.32 Examples and best practices for parallel API calls and OCR processing exist in various contexts.34
Project Implementations: Third-party projects integrating Mistral OCR, such as mcp-mistral-ocr 59 and pdf-ocr-obsidian 60, process multiple files, likely using sequential or parallel synchronous calls under the hood.
Explicit Looping Example: A blog post explicitly demonstrates iterating through a list of document URLs and calling client.ocr.process for each one, providing a basic structure that can be readily adapted for parallel execution.22
This convergence on parallel synchronous calls highlights it as the practical, albeit undocumented by Mistral as the official batch method, solution employed by developers.5. Clarifying the Batch OCR ImplementationBased on the evidence gathered from official documentation, the cookbook, and community experiences, we can clarify the status and intended method for batch OCR with Mistral AI.5.1. Definitive Statement on /v1/ocr Support via /v1/batch/jobsThe Mistral Batch API, accessed via the /v1/batch/jobs endpoint, does not support the /v1/ocr endpoint. This conclusion is firmly supported by:
The consistent omission of /v1/ocr from the documented list of supported endpoints for batch jobs.1
The OpenAPI specification, which does not list /v1/ocr as a valid value for the endpoint parameter in the POST /v1/batch/jobs request schema.1
The lack of a documented .jsonl format specific to OCR requests required for the Batch API.3
Attempting to create a batch job targeting /v1/ocr using client.batch.jobs.create or direct API calls is expected to fail, likely with a validation error (e.g., 422 Unprocessable Entity).5.2. Explanation of the Likely Intended/Supported MethodThe evidence strongly suggests that the intended and practical method for processing multiple documents with Mistral OCR is through parallel execution of synchronous /v1/ocr API calls. This approach involves using client-side concurrency mechanisms (like Python's concurrent.futures or asyncio) to issue multiple independent requests to the /v1/ocr endpoint simultaneously or near-simultaneously.This method aligns with:
The synchronous, single-document design of the /v1/ocr endpoint.2
The inferred implementation within the official batch_ocr.ipynb cookbook.5
Standard developer practices for batching requests to APIs lacking native batch support.22
Developers should architect their batch OCR solutions around this parallel synchronous call pattern.5.3. Addressing the "Batch Inference" DiscountA significant point of confusion stems from Mistral's marketing and pricing information, which repeatedly mentions a substantial discount (typically 50%, or "double the pages per dollar") for "batch inference" or "batch processing" applied to OCR.3 The standard Batch API also offers a discount.3Since /v1/ocr is incompatible with the /v1/batch/jobs endpoint, the discount advertised specifically for OCR cannot be obtained through the standard Batch API mechanism. The most logical interpretation is that Mistral intends this discount to apply to high-volume OCR processing achieved via parallel synchronous calls. The term "batch inference" in OCR marketing materials likely refers to this parallel processing pattern, not the Batch API endpoint itself.However, a critical gap exists: the mechanism for how this discount is triggered or applied for parallel synchronous OCR calls is undocumented. Standard OCR pricing is per page (e.g., $1 per 1000 pages 6). It is unclear if the discount is applied automatically based on volume thresholds detected by the API for a given key, or if it requires specific negotiation with Mistral sales or a different pricing tier. The API response for retrieving batch job status (GET /v1/batch/jobs/{job_id}) does not include cost information 3, and there are no documented methods in the client libraries to query costs programmatically.84Developers should not assume the 50% batch discount will be automatically applied when implementing parallel synchronous calls for OCR. Verification of the discount mechanism and eligibility should be sought directly from Mistral AI.6. Troubleshooting Guide for Mistral OCR Batch WorkflowsImplementing batch OCR using parallel synchronous calls requires careful handling of potential issues related to API limitations, concurrency, cost, and OCR quality.6.1. Common Problems CatalogDevelopers may encounter the following specific problems when building batch OCR workflows:
Job Creation Failures (Using Batch API): Attempting to use /v1/ocr as the endpoint in client.batch.jobs.create will fail.1
Input Data Formatting Issues (Parallel Sync): Errors related to incorrect file path handling, inaccessible URLs, improper base64 encoding, or failures in the two-step file upload process (upload + signed URL usage 17) within the parallel execution context.
Result Retrieval and Parsing Challenges (Parallel Sync): Difficulty aggregating results from multiple concurrent calls, handling exceptions or None returns from failed calls, parsing complex markdown output (especially tables 81), and managing embedded base64 image data.24
Cost Discrepancies: Being billed at the standard synchronous rate ($1/1000 pages 24) despite expecting the batch discount, due to the unclear application mechanism (See Section 5.3).
Performance Issues (Parallel Sync):

Hitting API rate limits (Requests Per Second or Tokens Per Minute 4) leading to 429 Too Many Requests errors.7
Individual /v1/ocr calls timing out due to large or complex documents.11
Overall slow processing if parallelization is inefficient or OCR itself is slow for certain inputs.86


OCR Quality Issues at Scale:

Systematic failures like returning image placeholders (![img-N.jpeg]) instead of text for scanned or image-heavy documents become major data quality problems when processing large batches.7
Other OCR errors (hallucinations, poor table/handwriting recognition 40) accumulate across batches.
Lack of confidence scores 7 makes programmatic quality filtering difficult.
Lack of text bounding boxes 46 hinders automated verification or correction workflows (though image bounding boxes are provided 17).


6.2. Table: Common Batch OCR Problems and Causes
ProblemLikely Cause(s)Batch Job Creation FailureUsing /v1/ocr with /v1/batch/jobs (unsupported endpoint 1).Unexpected High CostsBatch discount for OCR not applied automatically; unclear application mechanism.429 Too Many Requests ErrorsExceeding API rate limits (RPS/TPM) with parallel synchronous calls.4API Call TimeoutsLong processing time for individual large/complex documents via /v1/ocr.11OCR Results Missing Text (Image Placeholders)OCR model error/limitation in handling scanned documents, images within PDFs, or complex layouts.7Poor OCR Quality (Tables, Handwriting, etc.)Inherent limitations or potential hallucinations of the OCR model for specific content types.40Difficulty Parsing ResultsComplex markdown structure requires robust parsing logic; handling base64 images needs extra steps.24
6.3. Recommended Troubleshooting Steps and WorkaroundsDevelopers implementing parallel synchronous OCR workflows should consider the following:
Verify Endpoint Support: Confirm that /v1/ocr is not listed as supported for /v1/batch/jobs in the latest official documentation 1 and OpenAPI specification.1 Do not attempt to use the Batch API for OCR.
Validate Input Formats: Before submitting calls in parallel:

Ensure URLs are accessible.
Verify correct base64 encoding if sending image data directly.
Handle local file paths robustly.
If uploading files first, correctly implement the two-step process (upload, get signed URL, then call client.ocr.process with the URL 17) and manage potential errors in either step.


Implement Robust Error Handling:

Wrap calls to client.ocr.process (or its async equivalent) in try...except blocks.
Specifically catch potential API errors (e.g., mistralai.exceptions.MistralAPIException, httpx.HTTPStatusError for rate limits 9), network errors (httpx.RequestError), and timeouts (httpx.TimeoutException).
Implement a retry mechanism with exponential backoff for transient errors like rate limits (429) and server errors (5xx).9 Configure sensible maximum retries.
Check the content of successful responses for validity. Programmatically detect if the response contains only image placeholders (e.g., ![img-0.jpeg](img-0.jpeg)) instead of expected text, and treat these as failures.7
When using concurrent.futures or asyncio, ensure exceptions raised within tasks/futures are properly caught and handled upon result retrieval.32


Code Examples for Parallel Synchronous Processing:

Using concurrent.futures.ThreadPoolExecutor: (Suitable for I/O-bound tasks)
Pythonimport concurrent.futures
import os
from mistralai import Mistral
from mistralai.exceptions import MistralException
import time

# Initialize client (ensure MISTRAL_API_KEY is set)
client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))
ocr_model = "mistral-ocr-latest"

def process_single_document(doc_input):
    """Processes a single document URL or path, handles errors."""
    MAX_RETRIES = 3
    RETRY_DELAY = 2 # seconds

    for attempt in range(MAX_RETRIES):
        try:
            # Assuming doc_input is a URL for simplicity
            # Add logic here for file uploads if needed
            document_payload = {"type": "document_url", "document_url": doc_input}

            ocr_response = client.ocr.process(
                model=ocr_model,
                document=document_payload
                # Add include_image_base64=True if needed
            )

            # Basic check for placeholder error
            if ocr_response.pages and ocr_response.pages.markdown.strip().startswith("! # List of document URLs or paths
results = {}
MAX_WORKERS = 10 # Adjust based on rate limits and system resources

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    # Submit tasks
    future_to_doc = {executor.submit(process_single_document, doc): doc for doc in document_list}

    for future in concurrent.futures.as_completed(future_to_doc):
        doc_input = future_to_doc[future]
        try:
            input_ref, result_data = future.result()
            if result_data:
                results[input_ref] = result_data
                print(f"Successfully processed: {input_ref}")
            else:
                print(f"Failed to process: {input_ref}")
                # Handle failure (e.g., log, add to retry queue)
        except Exception as exc:
            print(f'{doc_input} generated an exception: {exc}')
            # Handle unexpected future exception

print(f"Finished processing. Successful results: {len(results)}/{len(document_list)}")
# Further processing of 'results' dictionary...


Using asyncio: (Requires async client methods or wrapping sync calls)
Pythonimport asyncio
import os
from mistralai import Mistral # Assuming an AsyncMistral client exists or use run_in_executor
from mistralai.exceptions import MistralException
import time

# Assume AsyncMistral client or wrap sync client
# client = AsyncMistral(api_key=os.environ.get("MISTRAL_API_KEY")) # Hypothetical
# OR use sync client with executor
sync_client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))
ocr_model = "mistral-ocr-latest"

async def process_single_document_async(doc_input, semaphore):
    """Async version of processing a single document with semaphore."""
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    async with semaphore: # Limit concurrency
        for attempt in range(MAX_RETRIES):
            try:
                document_payload = {"type": "document_url", "document_url": doc_input}

                # Use run_in_executor to run sync code in async context
                loop = asyncio.get_running_loop()
                ocr_response = await loop.run_in_executor(
                    None, # Use default ThreadPoolExecutor
                    sync_client.ocr.process,
                    ocr_model,
                    document_payload
                    # Add include_image_base64=True if needed
                )

                if ocr_response.pages and ocr_response.pages.markdown.strip().startswith("! # List of document URLs or paths
    results = {}
    MAX_CONCURRENT_TASKS = 10 # Control concurrency with semaphore

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    tasks = [process_single_document_async(doc, semaphore) for doc in document_list]

    for future in asyncio.as_completed(tasks):
        try:
            input_ref, result_data = await future
            if result_data:
                results[input_ref] = result_data
                print(f"Successfully processed: {input_ref}")
            else:
                print(f"Failed to process: {input_ref}")
                # Handle failure
        except Exception as exc:
            print(f'A task generated an exception: {exc}') # Should ideally be caught within task

    print(f"Finished processing. Successful results: {len(results)}/{len(document_list)}")
    # Further processing of 'results' dictionary...

# --- Run Async Main ---
# asyncio.run(main_async()) # Uncomment to run




Strategies for Managing Rate Limits and Costs:

Check your workspace's specific rate limits (RPS, Tokens/Minute) on the Mistral La Plateforme dashboard under "Limits".4
Implement client-side rate limiting in your parallel processing code. Use tools like asyncio.Semaphore (as shown above) or libraries like ratelimiter to ensure your aggregate request rate stays below the documented limits.
Monitor API usage and associated costs through the Mistral dashboard's billing section.82 Track spending against any set limits.
Crucially, contact Mistral AI support or sales to clarify how the 50% batch discount for OCR is applied. Do not assume it will be applied automatically to parallel synchronous calls. Understand the exact conditions and mechanism required to receive the discount.3


Improving OCR Quality:

Pre-processing: For scanned documents or images, apply pre-processing steps like deskewing, contrast enhancement, or binarization using libraries like OpenCV before sending them to the API.68 Ensure images have adequate resolution (e.g., >= 300 DPI).
Alternative Tools: If Mistral OCR consistently fails on specific document types (e.g., complex tables, handwriting, scanned images), consider using alternative specialized OCR tools (like marker-pdf 8, Azure Document Intelligence 38, or others mentioned in community discussions 94) either as a replacement or as part of an ensemble approach.42
Chat API Fallback: For extracting specific structured information (rather than full-document OCR), using the chat completion API (/v1/chat/completions) with the document URL provided as context might be more reliable, as reported by some users.38
Post-processing: Implement robust parsing logic for the returned markdown, potentially using dedicated markdown parsing libraries. Validate extracted data against expected formats or schemas.


7. ConclusionThe investigation confirms that Mistral AI's standard Batch API (/v1/batch/jobs) does not officially support the /v1/ocr endpoint. Documentation and API specifications consistently exclude OCR from the list of compatible batch operations.The recommended approach for developers needing to process multiple documents with Mistral OCR is to implement parallel execution of synchronous /v1/ocr API calls using client-side concurrency libraries such as Python's concurrent.futures or asyncio. The official batch_ocr.ipynb cookbook, despite its potentially confusing title, likely demonstrates this parallel synchronous method.However, developers pursuing this approach must be aware of several challenges:
OCR Quality: The underlying /v1/ocr endpoint exhibits reliability issues, particularly with scanned documents, images within PDFs, complex tables, and handwriting. Errors like returning image placeholders instead of text are frequently reported.
Lack of Quality Metrics: The API does not provide confidence scores for extracted text or bounding boxes for text elements, making automated quality assessment and verification difficult at scale.
Cost Ambiguity: While a 50% discount for "batch inference" on OCR is advertised, the mechanism for applying this discount to parallel synchronous calls is undocumented and unclear. Developers should not assume automatic application and should seek clarification from Mistral.
Error Handling & Rate Limiting: Robust error handling (including retries with backoff) and client-side rate limiting are essential to manage API errors, timeouts, and avoid exceeding workspace limits.
Final Recommendation: Developers should proceed with implementing batch OCR using parallel synchronous calls to the /v1/ocr endpoint. However, they must incorporate rigorous error handling, implement client-side rate limiting, carefully validate the quality and completeness of the OCR output, and proactively contact Mistral AI to clarify the application and eligibility criteria for the advertised batch processing discount for OCR. Evaluating alternative OCR solutions for specific problematic document types may also be necessary.