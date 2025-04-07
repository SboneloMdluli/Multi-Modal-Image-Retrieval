<template>
  <div class="app">
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-if="loading" class="loading-message">
      Searching for images...
    </div>
    <div class="image-grid">
      <div v-for="(image, index) in displayedImages" :key="index" class="image-card">
        <img :src="image.url" :alt="image.description" class="floating-image">
        <div class="caption-container">
          {{ image.caption }}
        </div>
      </div>
    </div>

    <div class="search-container">
      <div class="search-row">
        <textarea
          v-model="searchQuery"
          placeholder="Describe the images you want to find..."
          class="search-input"
          @keydown.enter.prevent="searchImages"
        ></textarea>
        <div class="count-container">
          <label for="image-count">Count:</label>
          <input
            id="image-count"
            type="number"
            v-model="imageCount"
            min="1"
            max="100"
            step="1"
            class="number-input"
            @change="handleCountChange"
          >
        </div>
      </div>
      <button @click="searchImages" class="search-button">Search Images</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      searchQuery: '',
      imageCount: 4,
      images: [],
      loading: false,
      error: null
    }
  },
  computed: {
    displayedImages() {
      return this.images.slice(0, this.imageCount);
    }
  },
  methods: {
    handleCountChange() {
      // Ensure imageCount stays within bounds
      if (this.imageCount < 1) {
        this.imageCount = 1;
      } else if (this.imageCount > 100) {
        this.imageCount = 100;
      }
      // Convert to integer to handle decimal inputs
      this.imageCount = Math.floor(Number(this.imageCount));
    },
    async searchImages() {
      console.log('searchImages called with:', {
        query: this.searchQuery,
        k: this.imageCount
      });

      this.loading = true;
      this.error = null;

      try {
        const url = `http://127.0.0.1:8000/api/v1/features/search?query=${encodeURIComponent(this.searchQuery)}&k=${this.imageCount}`;

        const response = await fetch(url);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (!data.results || data.results.length === 0) {
          throw new Error('No images found');
        }

        this.images = data.results.map(item => ({
          url: item.image_data,
          description: item.image_tag,
          caption: item.caption,
        }));

        console.log('Processed images array:', this.images);

      } catch (err) {
        this.error = `Error fetching images: ${err.message}`;
        this.images = [];
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style>
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.search-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.search-row {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.search-input {
  flex: 1;
  height: 50px;
  padding: 1rem;
  border: 2px solid #ddd;
  border-radius: 25px;
  resize: none;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  border-color: #4CAF50;
  outline: none;
}

.count-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.count-container label {
  font-size: 0.9rem;
  color: #666;
}

.number-input {
  width: 80px;
  padding: 0.5rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  text-align: center;
}

.search-button {
  padding: 1rem 2rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: #45a049;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.image-card {
  background: white;
  border-radius: 12px;
  box-shadow: rgba(0, 0, 0, 0.15) 0px 5px 15px 0px;
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.image-card:hover {
  transform: translateY(-5px);
  box-shadow: rgba(0, 0, 0, 0.25) 0px 15px 25px 0px;
}

.floating-image {
  width: 100%;
  height: 300px;
  object-fit: cover;
  display: block;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}

.caption-container {
  padding: 1.2rem;
  color: #ECF0F1;
  font-size: 0.95rem;
  line-height: 1.5;
  background-color: #34495E;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  flex-grow: 1;
  display: flex;
  align-items: center;
  min-height: 80px;
  text-align: center;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
}

.loading-message {
  background-color: #e3f2fd;
  color: #1565c0;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
}
</style>
