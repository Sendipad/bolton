import { createApp } from 'vue';
import App from './App.vue';
import { registerGlobalComponents } from "./globals.js";

/* import the necessary styles for Vue Flow to work */
import '@vue-flow/core/dist/style.css';
import '@vue-flow/core/dist/theme-default.css';
import '@vue-flow/controls/dist/style.css';
import '@vue-flow/minimap/dist/style.css';

class RuleBuilder {
    constructor({ wrapper, page, ruleName, documentType }) {
        this.$wrapper = $(wrapper);
        this.page = page;
        this.ruleName = ruleName;
        this.documentType = documentType;

        this.init();
    }

    init() {
        // set page title
        this.page.set_title(__('Editing {0}', [this.ruleName]));

        this.setup_page_actions();
        this.setup_app();
    }

    setup_page_actions() {
        // clear actions
        this.page.clear_actions();
        this.page.clear_menu();
        this.page.clear_custom_actions();

        // setup page actions
        this.primary_btn = this.page.set_primary_action(__("Save"), () => {
            if (this.app_instance) this.app_instance.saveRule();
        });

        this.test_btn = this.page.add_button(__("Test Rule"), () => {
            if (this.app_instance) this.app_instance.testRule();
        });

        this.go_to_form_btn = this.page.add_menu_item(__("Go to Rule Form"), () =>
            frappe.set_route("Form", "Rule", this.ruleName)
        );
    }

    setup_app() {
        // create a vue instance
        let app = createApp(App, {
            ruleName: this.ruleName,
            documentType: this.documentType,
            ref: (vm) => {
                this.app_instance = vm;
            }
        });

        // register global components
        registerGlobalComponents(app);

        // mount the app
        this.$rule_builder = app.mount(this.$wrapper.get(0));
        this.app = app;
    }

    destroy() {
        if (this.app) {
            this.app.unmount();
        }
    }
}

frappe.provide("frappe.ui");
frappe.ui.RuleBuilder = RuleBuilder;
export default RuleBuilder;
