document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('image-loader');
    const uploadWidget = document.getElementById('upload-widget');
    
    // Защита: если на странице нет самого виджета загрузки, выходим сразу
    if (!uploadWidget || !fileInput) return;

    const uploadText = uploadWidget.querySelector('.upload-text');
    const icon = uploadWidget.querySelector('.plus-icon');
    const headerRow = uploadWidget.querySelector('.upload-header-row');
    const actionBtn = uploadWidget.querySelector('.upload-action-btn'); // Вынесли в общие переменные
    
    const modal = document.getElementById('confirm-modal');
    let isImageLoaded = false;

    // Вспомогательная функция для полной очистки виджета (чтобы не дублировать код)
    const resetUploadWidget = () => {
        fileInput.value = ''; 
        const previewImg = uploadWidget.querySelector('.upload-preview');
        if (previewImg) previewImg.remove();
        uploadText.textContent = 'Загрузите изображение';
        if (icon) icon.classList.remove('is-cross'); 
        if (actionBtn) actionBtn.classList.remove('is-visible'); // Скрываем кнопку при удалении
        isImageLoaded = false;
    };

    // Функция закрытия модального окна (сработает только если модалка есть)
    const closeModal = () => {
        if (modal) modal.classList.remove('active');
        uploadWidget.style.cursor = 'pointer';
    };

    // 1. ИЗОЛИРУЕМ КЛИК ПО КНОПКЕ ДЕЙСТВИЯ (Чтобы не открывалась модалка)
    if (actionBtn) {
        actionBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // ОСТАНАВЛИВАЕТ всплытие события к uploadWidget
            
            // Здесь пишите ваш код, который должен происходить при отправке/действии:
            console.log('Кнопка действия нажата, файл готов к отправке:', fileInput.files[0]);
        });
    }

    // Перехватываем клик по кнопке-label
    uploadWidget.addEventListener('click', (e) => {
        if (isImageLoaded && e.target !== fileInput) {
            e.preventDefault(); 
            // Открываем модалку, только если она существует в HTML
            if (modal) {
                modal.classList.add('active');
                uploadWidget.style.cursor = 'default';
            } else {
                // Если модалки нет, просто очищаем инпут при повторном клике
                resetUploadWidget();
            }
        }
    });

    // Инициализируем события модалки только ЕCЛИ она есть на текущей странице
    if (modal) {
        const modalBox = modal.querySelector('.modal-box');
        const modalYes = document.getElementById('modal-yes');
        const modalNo = document.getElementById('modal-no');

        // Закрытие окна при клике на серое пустое пространство
        modal.addEventListener('click', (e) => {
            e.preventDefault();  
            e.stopPropagation();  
            closeModal();
        });

        // Запрещаем закрытие, если кликнули по самому белому окошку
        if (modalBox) {
            modalBox.addEventListener('click', (e) => {
                e.stopPropagation(); 
            });
        }

        // Кнопка "Да" в модалке
        if (modalYes) {
            modalYes.addEventListener('click', (e) => {
                e.stopPropagation(); 
                resetUploadWidget(); // Используем функцию очистки
                closeModal();
            });
        }

        // Кнопка "Нет" в модалке
        if (modalNo) {
            modalNo.addEventListener('click', (e) => {
                e.stopPropagation(); 
                closeModal();
            });
        }
    }

    // Обработка выбора файла (работает всегда независимо от модалки)
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const oldPreview = uploadWidget.querySelector('.upload-preview');
                if (oldPreview) oldPreview.remove();

                const img = document.createElement('img');
                img.src = e.target.result;
                img.classList.add('upload-preview');
                
                if (headerRow) headerRow.insertAdjacentElement('afterend', img);

                uploadText.textContent = 'Убрать изображение';
                if (icon) icon.classList.add('is-cross'); 
                isImageLoaded = true;

                if (actionBtn) actionBtn.classList.add('is-visible');
            };
            
            reader.readAsDataURL(this.files[0]);
        }
    });
});
