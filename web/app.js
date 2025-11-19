class GitHubTrendingDashboard {
    constructor() {
        this.repos = [];
        this.filteredRepos = [];
        this.currentPage = 1;
        this.itemsPerPage = 25;
        this.apiBaseUrl = window.location.hostname === 'localhost'
            ? 'http://localhost:8000/api/v1'
            : '/api/v1';

        this.init();
    }

    async init() {
        await this.loadLanguages();
        await this.loadRepositories();
        this.setupEventListeners();
    }

    async loadRepositories() {
        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/trending/latest?limit=1000`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.repos = await response.json();
            this.applyFilters();
            this.renderTable();
            this.updatePagination();

        } catch (error) {
            console.error('Error loading repositories:', error);
            this.showError('Failed to load repositories. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    async loadLanguages() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/trending/latest?limit=1000`);
            if (!response.ok) return;

            const repos = await response.json();
            const languages = [...new Set(repos.map(repo => repo.language).filter(Boolean))].sort();

            const languageFilter = document.getElementById('languageFilter');
            languageFilter.innerHTML = '<option value="">All Languages</option>';

            languages.forEach(language => {
                const option = document.createElement('option');
                option.value = language;
                option.textContent = language;
                languageFilter.appendChild(option);
            });

        } catch (error) {
            console.error('Error loading languages:', error);
        }
    }

    applyFilters() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const languageFilter = document.getElementById('languageFilter').value;
        const sortBy = document.getElementById('sortBy').value;

        this.filteredRepos = this.repos.filter(repo => {
            const matchesSearch = !searchTerm ||
                repo.repo_name.toLowerCase().includes(searchTerm) ||
                repo.description.toLowerCase().includes(searchTerm) ||
                repo.author.toLowerCase().includes(searchTerm);

            const matchesLanguage = !languageFilter || repo.language === languageFilter;

            return matchesSearch && matchesLanguage;
        });

        // Sort repositories
        this.filteredRepos.sort((a, b) => {
            switch (sortBy) {
                case 'stars_today':
                    return b.stars_today - a.stars_today;
                case 'total_stars':
                    return b.total_stars - a.total_stars;
                default:
                    return a.rank - b.rank;
            }
        });
    }

    renderTable() {
        const tbody = document.getElementById('reposTableBody');
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageRepos = this.filteredRepos.slice(startIndex, endIndex);

        tbody.innerHTML = pageRepos.map(repo => `
            <tr>
                <td class="fw-bold">#${repo.rank}</td>
                <td>
                    <div>
                        <a href="${repo.repo_url}" target="_blank" class="repo-link">
                            ${repo.repo_name}
                        </a>
                        <div class="author">by ${repo.author}</div>
                    </div>
                </td>
                <td>
                    <div class="description">${this.escapeHtml(repo.description || 'No description')}</div>
                </td>
                <td>
                    ${repo.language ? `<span class="language-badge bg-light text-dark">${this.escapeHtml(repo.language)}</span>` : '-'}
                </td>
                <td class="stars-today">
                    ${repo.stars_today > 0 ? `<i class="fas fa-star"></i> +${repo.stars_today.toLocaleString()}` : '-'}
                </td>
                <td class="total-stars">
                    <i class="fas fa-star"></i> ${repo.total_stars.toLocaleString()}
                </td>
            </tr>
        `).join('');
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredRepos.length / this.itemsPerPage);
        const prevPage = document.getElementById('prevPage');
        const nextPage = document.getElementById('nextPage');

        prevPage.classList.toggle('disabled', this.currentPage === 1);
        nextPage.classList.toggle('disabled', this.currentPage === totalPages);

        // Update page info
        const pageInfo = document.createElement('span');
        pageInfo.className = 'mx-3 align-self-center';
        pageInfo.textContent = `Page ${this.currentPage} of ${totalPages} (${this.filteredRepos.length} repos)`;

        const existingInfo = document.querySelector('.pagination .page-info');
        if (existingInfo) existingInfo.remove();

        prevPage.parentNode.insertBefore(pageInfo, nextPage);
    }

    setupEventListeners() {
        document.getElementById('searchInput').addEventListener('input', () => {
            this.currentPage = 1;
            this.applyFilters();
            this.renderTable();
            this.updatePagination();
        });

        document.getElementById('languageFilter').addEventListener('change', () => {
            this.currentPage = 1;
            this.applyFilters();
            this.renderTable();
            this.updatePagination();
        });

        document.getElementById('sortBy').addEventListener('change', () => {
            this.applyFilters();
            this.renderTable();
        });

        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadRepositories();
        });

        document.getElementById('prevPage').addEventListener('click', (e) => {
            e.preventDefault();
            if (this.currentPage > 1) {
                this.currentPage--;
                this.renderTable();
                this.updatePagination();
            }
        });

        document.getElementById('nextPage').addEventListener('click', (e) => {
            e.preventDefault();
            const totalPages = Math.ceil(this.filteredRepos.length / this.itemsPerPage);
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.renderTable();
                this.updatePagination();
            }
        });
    }

    showLoading(show) {
        document.getElementById('loadingSpinner').classList.toggle('d-none', !show);
    }

    showError(message) {
        // Simple error display - you could use a more sophisticated notification system
        alert(message);
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GitHubTrendingDashboard();
});