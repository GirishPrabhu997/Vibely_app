document.addEventListener("DOMContentLoaded", function () {
    // 1. Add Double-Click to Like Feature
    const postContainers = document.querySelectorAll(".post");

    postContainers.forEach(post => {
        const image = post.querySelector(".post-img");
        const likeBtn = post.querySelector(".like-btn");

        if (image && likeBtn) {
            image.addEventListener("dblclick", function () {
                // Instantly trigger the like button action anchor click
                likeBtn.click();
                
                // Optional: Create a quick popup heart overlay animation
                const heartOverlay = document.createElement("span");
                heartOverlay.innerHTML = "❤️";
                heartOverlay.style.position = "absolute";
                heartOverlay.style.top = "50%";
                heartOverlay.style.left = "50%";
                heartOverlay.style.transform = "translate(-50%, -50%) scale(0)";
                heartOverlay.style.fontSize = "5rem";
                heartOverlay.style.transition = "transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
                heartOverlay.style.pointerEvents = "none";
                
                if(!image.parentElement.querySelector('.heart-animated')) {
                    image.parentElement.appendChild(heartOverlay);
                    setTimeout(() => {
                        heartOverlay.style.transform = "translate(-50%, -50%) scale(1.2)";
                    }, 10);
                    setTimeout(() => {
                        heartOverlay.remove();
                    }, 500);
                }
            });
        }
    });

    // 2. Auto-scroll chat boxes to the absolute bottom on load
    const chatBox = document.querySelector(".chat-box");
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});