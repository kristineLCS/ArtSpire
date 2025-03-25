document.addEventListener("DOMContentLoaded", function () {
    // Ensure the "Generate" button fetches a prompt
    let generateBtn = document.getElementById("generate-btn");
    if (generateBtn) {
        generateBtn.addEventListener("click", function () {
            // Get category from data attribute on the page
            let category = document.getElementById("category-name").dataset.category;
            console.log("📌 Fetching prompt for category:", category);

            // Fetch the prompt based on the selected category
            fetch(`/get_prompt/?category=${encodeURIComponent(category)}`)
                .then(response => response.json())
                .then(data => {
                    console.log("✅ Received prompt:", data);
                    // Update the page with the received prompt
                    document.getElementById("prompt-text").innerText = data.prompt || "Error fetching prompt.";
                })
                .catch(error => console.error("❌ Error fetching prompt:", error));
        });
    }
});
