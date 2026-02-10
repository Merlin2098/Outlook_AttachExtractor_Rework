## Estructura del Proyecto

```
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── README.md
├── config/
│   ├── __init__.py
│   ├── app.ico
│   ├── config.json
│   ├── config_manager.py
│   ├── theme_dark.json
│   └── theme_light.json
├── core/
│   ├── __init__.py
│   ├── backend_base.py
│   ├── email_extractor.py
│   └── sign_classifier.py
├── generar_onedir.py
├── main.py
├── requirements.txt
├── runtime_hook_com.py
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── splash_screen.py
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── base_tab.py
│   │   ├── tab_clasificador.py
│   │   └── tab_extractor.py
│   ├── theme_manager.py
│   └── widgets/
│       ├── __init__.py
│       ├── author_info_widget.py
│       ├── base_widget.py
│       ├── date_range_widget.py
│       ├── folder_selector_widget.py
│       ├── outlook_folder_selector.py
│       ├── phrase_search_widget.py
│       ├── progress_widget.py
│       └── theme_toggle_widget.py
├── utils/
│   ├── __init__.py
│   ├── audit_mails.py
│   ├── date_handler.py
│   ├── logger.py
│   ├── notification_utils.py
│   └── power_manager.py
└── workers/
    ├── __init__.py
    ├── base_worker.py
    ├── classifier_worker.py
    └── extractor_worker.py
```
