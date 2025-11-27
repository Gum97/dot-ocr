/**
 * API Client for dots.ocr
 */

class DotsOCRAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    /**
     * Process a document (auto-detect type and convert if needed)
     */
    async processDocument(file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Add options
        if (options.promptMode) {
            formData.append('prompt_mode', options.promptMode);
        }
        
        if (options.fitzPreprocess !== undefined) {
            formData.append('fitz_preprocess', options.fitzPreprocess);
        }
        
        if (options.bbox) {
            formData.append('bbox', options.bbox);
        }

        try {
            const response = await fetch(`${this.baseURL}/api/v1/process`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Processing failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Check health status
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }

    /**
     * Get result file URL
     */
    getResultURL(path) {
        return `${this.baseURL}${path}`;
    }
}

// Export for use in app.js
window.DotsOCRAPI = DotsOCRAPI;
