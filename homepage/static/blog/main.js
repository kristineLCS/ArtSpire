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
      // Inside the .then() block after adding a new comment:
      if (data.success) {
        // Append the new comment to the comment list
        const commentList = document.querySelector(".comment-list");
        const noCommentMsg = document.querySelector(".no-comment-msg");

        // Remove "No comments yet." message if it exists
        if (noCommentMsg && noCommentMsg.parentNode) {
          noCommentMsg.parentNode.removeChild(noCommentMsg);
        }

        // Create the new comment element
        const newComment = document.createElement("div");
        newComment.classList.add("comment");
        newComment.innerHTML = `
          <strong>${data.name} - ${data.date_added}</strong>
          <p class="comment-body">${data.body}</p>
          <button class="edit-comment btn btn-sm btn-primary" data-comment-id="${data.comment_id}">Edit</button>
          <button class="delete-comment btn btn-sm btn-danger" data-comment-id="${data.comment_id}">Delete</button>
        `;
        
        // Add the comment to the comment list
        commentList.appendChild(newComment);
        
        // Clear input
        document.getElementById("id_body").value = "";
        
        // Reattach event listeners to the new Edit/Delete buttons
        attachEditListeners(newComment.querySelector(".edit-comment"));
        attachDeleteListeners(newComment.querySelector(".delete-comment"));
        
        // Remove error message (if any)
        errorMessageDiv.style.display = "none";

        // Update the "No comments yet" message
        updateNoCommentsMessage(); // <-- Call this function to update message visibility
      
      } else {
        errorMessageDiv.style.display = "block";
        errorMessageDiv.textContent = data.error || "Could not submit comment. Try again.";
      }
    })
  });
      

  // Update Comment
  document.querySelector(".comment-list").addEventListener("click", function(event) {
    const target = event.target;

    // Check if the clicked target is an edit button
    if (target && target.classList.contains("edit-comment")) {
      handleEdit(target); // Call function to handle edit
    } 
    // Check if clicked target is a delete button
    else if (target && target.classList.contains("delete-comment")) {
      handleDelete(target); // Call function to handle delete
    }
  });

  // Handle Edit Action
  function handleEdit(target) {
    const commentId = target.getAttribute("data-comment-id");
    const commentDiv = target.closest(".comment");
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

    // Create a text area for editing
    const textArea = document.createElement("textarea");
    textArea.value = commentText;
    textArea.rows = 3;
    textArea.classList.add("form-control");

    // Replace comment text with text area
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
            // Replace text area with updated comment text
            const updatedCommentBody = document.createElement("p");
            updatedCommentBody.classList.add("comment-body");
            updatedCommentBody.textContent = newBody;
            textArea.replaceWith(updatedCommentBody);
            saveButton.remove();
            cancelButton.remove();

            // Create and append new Edit and Delete buttons
            const newEditButton = document.createElement("button");
            newEditButton.textContent = "Edit";
            newEditButton.classList.add("edit-comment", "btn", "btn-sm", "btn-primary");
            newEditButton.setAttribute("data-comment-id", commentId);

            const newDeleteButton = document.createElement("button");
            newDeleteButton.textContent = "Delete";
            newDeleteButton.classList.add("delete-comment", "btn", "btn-sm", "btn-danger");
            newDeleteButton.setAttribute("data-comment-id", commentId);

            // Insert the new buttons after the updated comment text
            updatedCommentBody.appendChild(newEditButton);
            updatedCommentBody.appendChild(newDeleteButton);

            // Reattach event listeners to the new Edit/Delete buttons
            attachEditListeners(newEditButton);
            attachDeleteListeners(newDeleteButton);
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
  }

  // Handle Delete Action
  function handleDelete(target) {
    const commentId = target.getAttribute("data-comment-id");
    const commentDiv = target.closest(".comment");

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
    target.remove(); // remove original delete button

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

      fetch(deleteUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          commentDiv.remove();
        } else {
          console.error("❌ Error deleting comment:", data.error);
        }
      });
    });
  }

  function updateNoCommentsMessage() {
    const commentList = document.querySelector(".comment-list");
    const existingMsg = document.querySelector(".no-comment-msg");
  
    if (commentList.children.length === 0) {
      if (!existingMsg) {
        const msg = document.createElement("div");
        msg.classList.add("no-comment-msg");
        msg.innerHTML = "<p>No comments yet.</p>";
        commentList.parentNode.appendChild(msg);
      }
    } else {
      if (existingMsg) {
        existingMsg.remove();
      }
    }
  }
  

  
});
