document.addEventListener("DOMContentLoaded", function () {
  // NAVIGATION BAR
  const toggler = document.querySelector(".navbar-toggler");
  const collapse = document.querySelector("#navbarToggle");
  const closeBtn = document.querySelector("#closeSidebar");


  toggler.addEventListener("click", function() {
    collapse.classList.toggle("show");
  });

  closeBtn.addEventListener("click", function () {
    collapse.classList.remove("show");
    collapse.style.width = '0';
    collapse.style.display = 'none';
  });

  // Close sidebar when clicking outside of it
  document.addEventListener("click", function (event) {
    if (!collapse.contains(event.target) && !toggler.contains(event.target)) {
      collapse.classList.remove("show");
    }
  });


  // MESSAGE ALERT FADE OUT
  setTimeout(() => {
    const alerts = document.querySelectorAll('.popup-alert');
    alerts.forEach(alert => {
      alert.style.opacity = '0';
    });
  }, 8000); // 8 seconds

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


  // Comment section on Community Page
  document.getElementById("comment-form").addEventListener("submit", function(e) {
    e.preventDefault(); // Prevent full-page reload
  
    const commentBody = document.getElementById("id_body").value.trim();  // Get comment text
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    const errorMessageDiv = document.getElementById("error-message");
  
    // Clear previous errors
    errorMessageDiv.style.display = "none";
    errorMessageDiv.textContent = "";
  
    if (!commentBody) {
      errorMessageDiv.style.display = "block";
      errorMessageDiv.textContent = "Comment cannot be empty.";
      return;
    }
  
    const postId = document.getElementById("comment-form").dataset.postId;
    fetch(`/post/${postId}/comment/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrfToken,
      },
      body: `body=${encodeURIComponent(commentBody)}`
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Create the new comment HTML
        const newComment = document.createElement("div");
        newComment.classList.add("comment");
        newComment.innerHTML = `
          <strong>${data.name} - ${data.date_added}</strong>
          <p class="comment-body">${data.body}</p>
          <button class="edit-comment btn btn-sm btn-primary" data-comment-id="${data.comment_id}">Edit</button>
          <button class="delete-comment btn btn-sm btn-danger" data-comment-id="${data.comment_id}">Delete</button>
        `;

        // Append the new comment to the comment list
        document.getElementById("comments-section").appendChild(newComment);

        // Clear the comment input field
        document.getElementById("id_body").value = "";

        // Remove error message (if any)
        errorMessageDiv.style.display = "none";

        // Reattach event listeners to the new Edit/Delete buttons
        attachEditListeners(newComment.querySelector(".edit-comment"));
        attachDeleteListeners(newComment.querySelector(".delete-comment"));
  
      } else {
      errorMessageDiv.style.display = "block";
      errorMessageDiv.textContent = data.error || "Could not submit comment. Try again.";
    }
    })
  });
      

  // Update Comment
  document.querySelectorAll(".edit-comment").forEach(button => {
    button.addEventListener("click", function (e) {
      const commentId = e.target.getAttribute("data-comment-id");
      const commentDiv = e.target.parentNode;
      const commentBodyElement = commentDiv.querySelector(".comment-body");
      const editButton = commentDiv.querySelector(".edit-comment");
      const deleteButton = commentDiv.querySelector(".delete-comment");

      // Hide edit and delete buttons
      editButton.style.display = "none";
      deleteButton.style.display = "none";

      // Prevent multiple edit fields
      if (commentDiv.querySelector("textarea")) {
        return;
      }

    const commentText = commentBodyElement.textContent;

      // Create a textarea for editing
      const textArea = document.createElement("textarea");
      textArea.value = commentText;
      textArea.rows = 3;
      textArea.classList.add("form-control");

      // Replace comment text with textarea
      commentBodyElement.replaceWith(textArea);

      // Create Save and Cancel buttons
      const saveButton = document.createElement("button");
      saveButton.textContent = "Save";
      saveButton.classList.add("save-edit", "btn", "btn-sm", "btn-success", "mx-1");

      const cancelButton = document.createElement("button");
      cancelButton.textContent = "Cancel";
      cancelButton.classList.add("cancel-edit", "btn", "btn-sm", "btn-secondary");

      // Append buttons only once
      commentDiv.appendChild(saveButton);
      commentDiv.appendChild(cancelButton);

      // Save button functionality
      saveButton.addEventListener("click", function () {
        const newBody = textArea.value.trim();
        if (newBody) {
          fetch(`/comment/${commentId}/edit/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({ body: newBody }),
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Replace textarea with updated comment text
            const updatedCommentBody = document.createElement("p");
            updatedCommentBody.classList.add("comment-body");
            updatedCommentBody.textContent = newBody;
            textArea.replaceWith(updatedCommentBody);
            saveButton.remove();
            cancelButton.remove();
                
            // Show edit and delete buttons again
            editButton.style.display = "inline-block";
            deleteButton.style.display = "inline-block";
          } else {
            console.error("Error updating comment:", data.error);
          }
          });
        }
      });

      // Cancel button functionality
      cancelButton.addEventListener("click", function () {
        const originalCommentBody = document.createElement("p");
        originalCommentBody.classList.add("comment-body");
        originalCommentBody.textContent = commentText;
        textArea.replaceWith(originalCommentBody);
        saveButton.remove();
        cancelButton.remove();

        // Show edit and delete buttons again
        editButton.style.display = "inline-block";
        deleteButton.style.display = "inline-block";
      });
    });
  });



  // Function to display error messages
  function showError(message) {
    const errorDiv = document.getElementById("error-message");
    errorDiv.style.display = "block";
    errorDiv.textContent = message;
  }



  // Delete Comment
  document.querySelectorAll(".delete-comment").forEach(button => {
    button.addEventListener("click", function(e) {
      const commentId = e.target.getAttribute("data-comment-id");

      if (!commentId) {
        console.error("❌ No comment ID found. Check your HTML!");
        return;
      }

      const commentDiv = e.target.parentNode;
      console.log("🛠️ Debug: commentDiv =", commentDiv);

      // Show a confirmation message instead of the Delete button
      const confirmDiv = document.createElement("div");
      confirmDiv.classList.add("confirmation-message");

      const confirmText = document.createElement("p");
      confirmText.textContent = "Are you sure you want to delete this comment?";

      const confirmButton = document.createElement("button");
      confirmButton.textContent = "Confirm";
      confirmButton.classList.add("btn", "btn-sm", "btn-danger");

      const cancelButton = document.createElement("button");
      cancelButton.textContent = "Cancel";
      cancelButton.classList.add("btn", "btn-sm", "btn-secondary");

      confirmDiv.appendChild(confirmText);
      confirmDiv.appendChild(confirmButton);
      confirmDiv.appendChild(cancelButton);

      commentDiv.appendChild(confirmDiv);
      e.target.remove(); // Remove the original delete button

      cancelButton.addEventListener("click", function() {
        confirmDiv.remove();
        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.classList.add("delete-comment", "btn", "btn-sm", "btn-danger");
        deleteButton.setAttribute("data-comment-id", commentId);
        commentDiv.appendChild(deleteButton);
      });

      confirmButton.addEventListener("click", function() {
        const deleteUrl = `/comment/${commentId}/delete/`;  // Constructed URL
        console.log("🛠️ Debug: Sending DELETE request to", deleteUrl);
    
        fetch(deleteUrl, {  
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
          },
          })
          .then(response => response.json())
          .then(data => {
            console.log("🛠️ Debug: Response from server:", data);  // Check server response
            if (data.success) {
              commentDiv.remove();
            } else {
              console.error("❌ Error deleting comment:", data.error);
            }
          })
          .catch(error => {
            console.error("❌ Fetch error:", error);
          });
      });
    });
  });

  
});
