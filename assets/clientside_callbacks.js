window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_theme: function(switch_on, stored_theme_data) {
            // These URLs should be dynamically fetched or explicitly set.
            // For this example, we are using placeholders that will be replaced
            // by the Python script that registers the callback.
            // However, for a direct assets file, these would be hardcoded or
            // fetched via another mechanism if dynamic URLs are strictly needed.
            // For now, let's assume they are passed via the registration in Python.
            // If this JS is directly in assets, it needs actual URLs.
            // For the purpose of this task, we'll assume the Python registration
            // will handle injecting the correct URLs.
            const theme_urls = {
                light: dash_clientside.callback_context.custom_data.FLATLY_URL, // Passed via custom_data
                dark: dash_clientside.callback_context.custom_data.DARKLY_URL   // Passed via custom_data
            };
            var new_theme_mode = null;
            var new_switch_state = false;
            var new_href = theme_urls.light;

            const triggered_inputs = window.dash_clientside.callback_context.triggered;
            var triggered_input_id = null;
            if (triggered_inputs && triggered_inputs.length > 0) {
                triggered_input_id = triggered_inputs[0].prop_id;
            }
            
            // Initial load or no specific trigger means we check stored_theme_data first or default to light
            if (!triggered_input_id && stored_theme_data && stored_theme_data.theme) {
                 new_theme_mode = stored_theme_data.theme;
                 new_switch_state = new_theme_mode === "dark";
            } else if (triggered_input_id === "theme-switch.value") {
                new_theme_mode = switch_on ? "dark" : "light";
                new_switch_state = switch_on;
            } else if (stored_theme_data && stored_theme_data.theme) { // Fallback to stored if available (e.g. initial load)
                new_theme_mode = stored_theme_data.theme;
                new_switch_state = new_theme_mode === "dark";
            } else { // Default initialization
                new_theme_mode = "light";
                new_switch_state = false;
            }

            new_href = theme_urls[new_theme_mode] || theme_urls.light;
            
            // console.log("Triggered:", triggered_input_id, "Switch:", switch_on, "Stored:", stored_theme_data, "New Mode:", new_theme_mode, "New Href:", new_href);

            return [new_href, {theme: new_theme_mode}, new_switch_state];
        }
    }
});
