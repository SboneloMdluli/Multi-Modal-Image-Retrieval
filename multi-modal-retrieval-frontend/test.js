        const response = await fetch('http://localhost:8000/api/v1/features/features/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: "gassed",
            num_images: 4
          })
        });
