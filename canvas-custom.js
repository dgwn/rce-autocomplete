// ---------------------------------------------------------------
// Upload this script to your Canvas Theme's Custom JS section
// or append it to the end of an existing custom JS file
// to enable the autocomplete feature in the Rich Content Editor.
// ---------------------------------------------------------------

let editor;

const editorIds = [
  "assignment_description",
  "wiki_page_body",
  "discussion-topic-message2"
];

const findEditorInstance = async () => {
  const maxAttempts = 5; // 2.5 seconds
  let attempts = 0;

  while (attempts < maxAttempts) {
    for (const id of editorIds) {
      const instance = tinymce.get(id);
      if (instance) {
        editor = instance;
        return;
      }
    }
    attempts++;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
};

findEditorInstance().then(() => {
  if (editor) {
    const onAction = (autocompleteApi, rng, value) => {
      editor.selection.setRng(rng);
      editor.insertContent(value);
      autocompleteApi.hide();
    };

    let getContentUntilCarat = () => {
      const selection = editor.selection;
      const rng = selection.getRng();
      const startContainer = rng.startContainer;
      const startOffset = rng.startOffset;

      let textBeforeCaret = "";

      const walker = document.createTreeWalker(
        editor.getBody(),
        NodeFilter.SHOW_TEXT,
        null,
        false
      );

      let node;
      while ((node = walker.nextNode())) {
        if (node === startContainer) {
          textBeforeCaret += node.textContent.substring(0, startOffset);
          break;
        } else {
          textBeforeCaret += node.textContent;
        }
      }

      return {
        textBeforeCaret,
        fullContext: editor.getContent()
      };
    };

    editor.ui.registry.addAutocompleter("autocomplete", {
      ch: "~",
      minChars: 0,
      columns: "auto",
      onAction: onAction,
      fetch: (pattern) => {
        return new Promise((resolve) => {
          const contentUntilCarat = getContentUntilCarat();
          fetch(
            "https://<your-api-domain-here>/api/completion/dummy-complete",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                content_up_until_cursor: contentUntilCarat.textBeforeCaret,
                all_content_in_rce: contentUntilCarat.fullContext
              })
            }
          )
            .then((response) => response.json())
            .then((data) => {
              const results = [
                {
                  type: "autocompleteitem",
                  value: data.suggestion,
                  text: "Generate!",
                  icon: data.suggestion
                }
              ];
              resolve(results);
            })
            .catch((error) => {
              console.error("Error:", error);
              resolve([]);
            });
        });
      }
    });
  } else {
    console.log("No editor instance found after 2.5 seconds.");
  }
});

// ---------------------------------------------------------------
// Custom CSS to override the tinyMCE styles
// ---------------------------------------------------------------

const style = document.createElement("style");
style.innerHTML = `
  .tox-collection__item-icon {
    max-width: 50rem !important;
    max-height: 50rem !important;
    width: auto !important;
    height: auto !important;

  }
  .tox-autocompleter {
    max-width: 50rem !important;
    max-height: 50rem !important;
    width: auto !important;
    height: auto !important;
  }
  .tox-menu {
    max-width: 50rem !important;
    max-height: 50rem !important;
    width: auto !important;
    height: auto !important;
  }
  .tox-collection__group {
    max-width: 50rem !important;
    max-height: 50rem !important;
    width: auto !important;
    height: auto !important;
  } 
`;
document.head.appendChild(style);

// ---------------------------------------------------------------
// AI BUTTON
// ---------------------------------------------------------------

// Create the AI button
const newButton = document.createElement("button");
newButton.title = "AI";
newButton.ariaLabel = "AI";
newButton.type = "button";
newButton.unselectable = "on";
newButton.tabIndex = -1;
newButton.className = "tox-tbtn tox-tbtn--select tox-tbtn--bespoke";
newButton.style.userSelect = "none";
newButton.onclick = () => (modal.style.display = "block");

const newSpan = document.createElement("span");
newSpan.className = "tox-tbtn__select-label";
newSpan.textContent = "AI";
newButton.appendChild(newSpan);

const existingButton = document.querySelector(".tox-tbtn--select");
existingButton.parentNode.insertBefore(newButton, existingButton.nextSibling);

// Create the modal structure
const modal = document.createElement("div");
modal.className = "modal";
modal.style.display = "none";
modal.style.position = "fixed";
modal.style.zIndex = "999";
modal.style.left = "0";
modal.style.top = "0";
modal.style.width = "100%";
modal.style.height = "100%";
modal.style.overflow = "auto";
modal.style.backgroundColor = "rgba(0,0,0,0.4)";

const modalContent = document.createElement("div");
modalContent.className = "modal-content";
modalContent.style.backgroundColor = "#fefefe";
modalContent.style.margin = "15% auto";
modalContent.style.padding = "20px";
modalContent.style.border = "1px solid #888";
modalContent.style.width = "80%";

const closeButton = document.createElement("span");
closeButton.className = "close";
closeButton.innerHTML = "&times;";
closeButton.style.color = "#aaa";
closeButton.style.float = "right";
closeButton.style.fontSize = "28px";
closeButton.style.fontWeight = "bold";
closeButton.style.cursor = "pointer";
closeButton.onclick = () => closeModal();

const promptText = document.createElement("p");
promptText.textContent = "What are you looking for";

const inputBox = document.createElement("input");
inputBox.type = "text";
inputBox.style.width = "100%";
inputBox.style.padding = "12px 20px";
inputBox.style.margin = "8px 0";
inputBox.style.boxSizing = "border-box";

const submitButton = document.createElement("button");
submitButton.textContent = "Submit";
submitButton.style.padding = "10px 20px";
submitButton.style.marginTop = "10px";
submitButton.style.cursor = "pointer";
submitButton.onclick = () => handleSubmit();

const hr = document.createElement("hr");

const insertPrompt = document.createElement("p");
insertPrompt.textContent = "You can insert the following content.";
insertPrompt.style.marginTop = "20px";
insertPrompt.style.display = "none";
insertPrompt.id = "insertPrompt";

const resultText = document.createElement("p");
resultText.id = "resultText";
resultText.style.marginTop = "10px";
resultText.style.display = "none";

const insertButton = document.createElement("button");
insertButton.id = "insertButton";
insertButton.textContent = "Insert";
insertButton.style.padding = "10px 20px";
insertButton.style.marginTop = "10px";
insertButton.style.cursor = "pointer";
insertButton.style.display = "none";
insertButton.onclick = () => handleInsert();

// Append elements to modal content
modalContent.appendChild(closeButton);
modalContent.appendChild(promptText);
modalContent.appendChild(inputBox);
modalContent.appendChild(submitButton);
modalContent.appendChild(hr);
modalContent.appendChild(insertPrompt);
modalContent.appendChild(resultText);
modalContent.appendChild(insertButton);

// Append modal content to modal
modal.appendChild(modalContent);

// Append modal to document body
document.body.appendChild(modal);

const closeModal = () => {
  modal.style.display = "none";
  document.getElementById("resultText").style.display = "none";
  document.getElementById("insertButton").style.display = "none";
  document.getElementById("insertPrompt").style.display = "none";
  modal.querySelector("input").value = "";
};

const handleSubmit = async () => {
  const userInput = modal.querySelector("input").value;
  const editorContent = editor.getContent();
  const result = await processInput(userInput, editorContent);
  const resultText = document.getElementById("resultText");
  resultText.textContent = result;
  resultText.style.display = "block";
  document.getElementById("insertButton").style.display = "block";
  document.getElementById("insertPrompt").style.display = "block";
};

const processInput = async (userInput, editorContent) => {
  try {
    const response = await fetch("https://<your-api-domain-here>/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        userInput,
        editorContent
      })
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await response.json();
    return data.html; // Assuming the response contains a field named 'response'
  } catch (error) {
    console.error("Error:", error);
    return "Error processing input";
  }
};

const handleInsert = () => {
  editor.insertContent(document.getElementById("resultText").textContent);
  closeModal();
};

window.addEventListener("click", (event) => {
  if (event.target === modal) closeModal();
});
