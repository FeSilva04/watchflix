document.addEventListener('DOMContentLoaded', function() {
    const carousels = document.querySelectorAll('.item-carousel');
    
    carousels.forEach(carousel => {
        const container = carousel.parentElement;
        const prevBtn = container.querySelector('.prev-btn');
        const nextBtn = container.querySelector('.next-btn');
        const card = carousel.querySelector('.item-card');
        
        if (!card) return;
        
        const cardWidth = card.offsetWidth + parseInt(getComputedStyle(carousel).gap);
        const scrollAmount = cardWidth * 2; // Avança 2 cards por clique
        
        // Navegação
        nextBtn.addEventListener('click', () => {
            carousel.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        });
        
        prevBtn.addEventListener('click', () => {
            carousel.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        });
        
        // Atualizar visibilidade dos botões
        const updateButtons = () => {
            prevBtn.style.display = carousel.scrollLeft > 10 ? 'flex' : 'none';
            nextBtn.style.display = carousel.scrollLeft < 
                (carousel.scrollWidth - carousel.clientWidth - 10) ? 'flex' : 'none';
        };
        
        // Inicializar
        updateButtons();
        
        // Atualizar no scroll
        carousel.addEventListener('scroll', updateButtons);
        
        // Atualizar no redimensionamento
        window.addEventListener('resize', updateButtons);
        
        // Touch events para mobile
        let isDragging = false;
        let startX, scrollLeft;
        
        carousel.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.pageX - carousel.offsetLeft;
            scrollLeft = carousel.scrollLeft;
            carousel.style.cursor = 'grabbing';
            carousel.style.scrollBehavior = 'auto';
        });
        
        carousel.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            e.preventDefault();
            const x = e.pageX - carousel.offsetLeft;
            const walk = (x - startX) * 2;
            carousel.scrollLeft = scrollLeft - walk;
        });
        
        window.addEventListener('mouseup', () => {
            isDragging = false;
            carousel.style.cursor = 'grab';
            carousel.style.scrollBehavior = 'smooth';
        });
    });
});