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
          fetch("https://<you-api-domain-here>/api/completion/dummy-complete", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              content_up_until_cursor: contentUntilCarat.textBeforeCaret,
              all_content_in_rce: contentUntilCarat.fullContext
            })
          })
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
