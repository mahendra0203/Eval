import json
import argparse
from openai import OpenAI

def read_prompts_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['prompts']

def make_model_call(client, model, content):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=300
        )
        return {
            "success": True,
            "response": response,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "response": None,
            "error": str(e)
        }

def process_prompts(client, prompts, models):
    all_results = []
    for prompt in prompts:
        prompt_results = []
        for model in models:
            print(f"Processing prompt {prompts.index(prompt) + 1}/{len(prompts)} with model: {model}")
            api_res = make_model_call(client, model, prompt)
            prompt_results.append({"model_name": model, "response": api_res})
        all_results.append({"prompt": prompt, "results": prompt_results})
    return all_results

def generate_html_report_tailwind_2(all_results):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vision Model Comparison - Multiple Prompts</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            clifford: '#da373d',
                        }
                    }
                }
            }
        </script>
        <style type="text/tailwindcss">
            @layer utilities {
                .content-auto {
                    content-visibility: auto;
                }
            }
        </style>
        <style>
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0,0,0,0.9);
            }
            .modal-content {
                margin: auto;
                display: block;
                width: 80%;
                max-width: 700px;
            }
            .close {
                position: absolute;
                top: 15px;
                right: 35px;
                color: #f1f1f1;
                font-size: 40px;
                font-weight: bold;
                transition: 0.3s;
            }
            .close:hover,
            .close:focus {
                color: #bbb;
                text-decoration: none;
                cursor: pointer;
            }
        </style>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-4xl font-bold mb-8 text-center text-blue-600">OpenAI Vision Model Comparison</h1>
    """

    for prompt_index, prompt_result in enumerate(all_results, 1):
        prompt = prompt_result["prompt"]
        text_content = ' '.join([item["text"] for item in prompt if item["type"] == "text"])
        image_content = ''.join([
            f'''
            <div class="inline-block">
                <img src="{item["image_url"]["url"]}" alt="Prompt Image" class="max-w-[240px] h-auto rounded-none shadow-lg m-2 cursor-pointer" onclick="openModal(this.src)">
            </div>
            '''
            for item in prompt if item["type"] == "image_url"
        ])
        prompt_html = f'<p class="mb-4">{text_content}</p><div class="flex flex-wrap">{image_content}</div>'

        html_content += f"""
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-semibold mb-4">Prompt {prompt_index}:</h2>
            <div class="mb-6">
                {prompt_html}
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        """

        for result in prompt_result["results"]:
            model_response = result['response']['response'].choices[0].message.content if result['response'] and result['response']['success'] else 'N/A'
            api_response = json.dumps(result['response']['response'].model_dump() if result['response'] and result['response']['success'] else {}, indent=2)
            error_details = result['response']['error'] if result['response'] and not result['response']['success'] else 'N/A'

            html_content += f"""
            <div class="bg-gray-50 rounded-lg p-4">
                <h3 class="text-xl font-semibold mb-2 text-blue-500">{result['model_name']}</h3>
                <div class="mb-4">
                    <h4 class="font-medium text-gray-700 mb-1">Model Response:</h4>
                    <p class="text-sm bg-white p-2 rounded">{model_response}</p>
                </div>
                <details class="mb-4">
                    <summary class="cursor-pointer text-sm font-medium text-gray-700">Full API Response</summary>
                    <pre class="text-xs bg-white p-2 rounded mt-2 overflow-x-auto">{api_response}</pre>
                </details>
                <div>
                    <h4 class="font-medium text-gray-700 mb-1">Error Details:</h4>
                    <p class="text-sm text-red-500">{error_details}</p>
                </div>
            </div>
            """

        html_content += """
            </div>
        </div>
        """

    html_content += """
        </div>
        <div id="imageModal" class="modal">
            <span class="close" onclick="closeModal()">&times;</span>
            <img class="modal-content" id="modalImage">
        </div>
        <script>
            function openModal(imageSrc) {
                var modal = document.getElementById("imageModal");
                var modalImg = document.getElementById("modalImage");
                modal.style.display = "block";
                modal.style.alignContent = "center";
                modalImg.src = imageSrc;
            }

            function closeModal() {
                var modal = document.getElementById("imageModal");
                modal.style.display = "none";
            }

            window.onclick = function(event) {
                var modal = document.getElementById("imageModal");
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }

            document.addEventListener('DOMContentLoaded', (event) => {
                document.querySelectorAll('details').forEach((el) => {
                    el.addEventListener('toggle', (e) => {
                        if (el.open) {
                            const preElement = el.querySelector('pre');
                            if (preElement) {
                                const codeContent = preElement.textContent;
                                try {
                                    const formattedContent = JSON.stringify(JSON.parse(codeContent), null, 2);
                                    preElement.textContent = formattedContent;
                                } catch (error) {
                                    console.error('Error parsing JSON:', error);
                                }
                            }
                        }
                    });
                });
            });
        </script>
    </body>
    </html>
    """
    return html_content

def main():
    parser = argparse.ArgumentParser(description="OpenAI Vision Model Comparison")
    parser.add_argument("--prompts_file", required=True, help="Path to the JSON file containing prompts")
    parser.add_argument("--openai_api_key", required=True, help="OpenAI API Key")
    parser.add_argument("--output_file", default="vision_model_comparison_report.html", help="Output HTML file name")
    

    args = parser.parse_args()

    client = OpenAI(api_key=args.openai_api_key)
    
    openai_vision_models =['gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini']

    try:
        prompts = read_prompts_from_file(args.prompts_file)
        all_results = process_prompts(client, prompts, openai_vision_models)
        html_report = generate_html_report_tailwind_2(all_results)

        output_file = "vision_model_comparison_report.html"
        with open(output_file, "w") as f:
            f.write(html_report)

        print(f"HTML report generated: {output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
  main()