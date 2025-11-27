/**
 * Main application logic
 */

const api = new DotsOCRAPI();
let selectedFile = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectFileBtn = document.getElementById('selectFileBtn');
const filePreview = document.getElementById('filePreview');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFileBtn = document.getElementById('removeFileBtn');
const processBtn = document.getElementById('processBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const promptMode = document.getElementById('promptMode');
const fitzPreprocess = document.getElementById('fitzPreprocess');
const bboxGroup = document.getElementById('bboxGroup');
const bbox = document.getElementById('bbox');

// Initialize
init();

function init() {
    // Click to select file
    selectFileBtn.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('click', (e) => {
        if (e.target === uploadArea || e.target.closest('.upload-icon, h3, p')) {
            fileInput.click();
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFileSelect(e.dataTransfer.files[0]);
    });

    // Remove file
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });

    // Process button
    processBtn.addEventListener('click', processDocument);

    // Prompt mode change
    promptMode.addEventListener('change', (e) => {
        // Show bbox input for grounding OCR
        if (e.target.value === 'prompt_grounding_ocr') {
            bboxGroup.style.display = 'block';
        } else {
            bboxGroup.style.display = 'none';
        }
    });

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            switchTab(tab);
        });
    });

    // Check API health on load
    checkHealth();
}

function handleFileSelect(file) {
    if (!file) return;

    // Validate file type
    const validExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.docx', '.doc'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();

    if (!validExtensions.includes(fileExt)) {
        alert('File không được hỗ trợ! Vui lòng chọn PDF, Image, hoặc DOCX.');
        return;
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
        alert('File quá lớn! Vui lòng chọn file nhỏ hơn 50MB.');
        return;
    }

    selectedFile = file;

    // Show preview
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    filePreview.style.display = 'block';
    uploadArea.style.display = 'none';
    processBtn.disabled = false;
}

function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    filePreview.style.display = 'none';
    uploadArea.style.display = 'block';
    processBtn.disabled = true;
    resultsSection.style.display = 'none';
}

async function processDocument() {
    if (!selectedFile) return;

    // Hide results, show progress
    resultsSection.style.display = 'none';
    progressSection.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Đang tải lên...';
    processBtn.disabled = true;

    // Simulate progress (since we don't have real progress)
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressFill.style.width = progress + '%';
    }, 500);

    try {
        progressText.textContent = 'Đang xử lý...';

        const options = {
            promptMode: promptMode.value,
            fitzPreprocess: fitzPreprocess.checked
        };

        // Add bbox if in grounding mode
        if (promptMode.value === 'prompt_grounding_ocr' && bbox.value) {
            options.bbox = bbox.value;
        }

        const result = await api.processDocument(selectedFile, options);

        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressText.textContent = 'Hoàn thành!';

        setTimeout(() => {
            progressSection.style.display = 'none';
            displayResults(result);
        }, 500);

    } catch (error) {
        clearInterval(progressInterval);
        progressSection.style.display = 'none';
        alert('Lỗi xử lý: ' + error.message);
        console.error(error);
    } finally {
        processBtn.disabled = false;
    }
}

function displayResults(result) {
    resultsSection.style.display = 'block';

    // Display info
    const infoHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div>
                <strong>Trạng thái:</strong> ${result.status}
            </div>
            <div>
                <strong>Loại file:</strong> ${result.file_type}
            </div>
            ${result.total_pages ? `<div><strong>Số trang:</strong> ${result.total_pages}</div>` : ''}
            ${result.processing_time ? `<div><strong>Thời gian:</strong> ${result.processing_time.toFixed(2)}s</div>` : ''}
            ${result.device_used ? `<div><strong>Device:</strong> ${result.device_used}</div>` : ''}
            ${result.layout_elements ? `<div><strong>Elements:</strong> ${result.layout_elements.length}</div>` : ''}
        </div>
    `;
    document.getElementById('resultInfo').innerHTML = infoHTML;

    // Display markdown
    if (result.markdown_content) {
        document.getElementById('markdownPreview').innerHTML = marked.parse(result.markdown_content);
    }

    // Display layout image
    if (result.layout_image_url) {
        const img = document.getElementById('layoutImage');
        img.src = api.getResultURL(result.layout_image_url);
    }

    // Display JSON
    if (result.layout_elements) {
        document.getElementById('jsonPreview').textContent = JSON.stringify(result.layout_elements, null, 2);
    }

    // Download button
    document.getElementById('downloadBtn').onclick = () => {
        if (result.markdown_url) {
            window.open(api.getResultURL(result.markdown_url), '_blank');
        }
    };

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName + 'Tab').classList.add('active');
}

async function checkHealth() {
    try {
        const health = await api.healthCheck();
        console.log('API Health:', health);

        if (!health.model_loaded) {
            console.warn('Model not loaded yet. It will be loaded on first request.');
        }
    } catch (error) {
        console.error('API không khả dụng:', error);
        alert('Không thể kết nối đến API server. Vui lòng kiểm tra xem server đã chạy chưa.');
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
