import React, { useState, useEffect } from "react";
import { X, Save, RotateCcw, Loader2 } from "lucide-react";
import { api } from "../api";
import "./Settings.css";

const Settings = ({ isOpen, onClose }) => {
    const [email, setEmail] = useState("");
    const [customPrompt, setCustomPrompt] = useState("");
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState({ type: "", text: "" });

    // Default prompt for display reference
    const defaultPromptPreview = `You are an expert Legal AI Assistant specializing in Pakistani law...

(This is the default prompt. Leave the field empty to use it, or enter your own custom prompt.)`;

    // Fetch settings on mount
    useEffect(() => {
        if (isOpen) {
            fetchSettings();
        }
    }, [isOpen]);

    const fetchSettings = async () => {
        setLoading(true);
        try {
            const data = await api.getSettings();
            setEmail(data.email || "");
            setCustomPrompt(data.custom_prompt || "");
        } catch (err) {
            console.error("Failed to load settings:", err);
            setMessage({ type: "error", text: "Failed to load settings" });
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        setMessage({ type: "", text: "" });
        try {
            await api.savePrompt(customPrompt || null);
            setMessage({ type: "success", text: "Prompt saved successfully!" });
            setTimeout(() => setMessage({ type: "", text: "" }), 3000);
        } catch (err) {
            console.error("Failed to save prompt:", err);
            setMessage({ type: "error", text: "Failed to save prompt" });
        } finally {
            setSaving(false);
        }
    };

    const handleReset = async () => {
        setSaving(true);
        setMessage({ type: "", text: "" });
        try {
            await api.resetPrompt();
            setCustomPrompt("");
            setMessage({ type: "success", text: "Reset to default prompt!" });
            setTimeout(() => setMessage({ type: "", text: "" }), 3000);
        } catch (err) {
            console.error("Failed to reset prompt:", err);
            setMessage({ type: "error", text: "Failed to reset prompt" });
        } finally {
            setSaving(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="settings-overlay" onClick={onClose}>
            <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="settings-header">
                    <h2>Settings</h2>
                    <button className="close-btn" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                {loading ? (
                    <div className="settings-loading">
                        <Loader2 className="animate-spin" size={24} />
                        <span>Loading settings...</span>
                    </div>
                ) : (
                    <div className="settings-content">
                        {/* User Info Section */}
                        <div className="settings-section">
                            <h3>Account</h3>
                            <div className="field-group">
                                <label>Email</label>
                                <input type="text" value={email} disabled className="field-input disabled" />
                            </div>
                        </div>

                        {/* Custom Prompt Section */}
                        <div className="settings-section">
                            <h3>Custom System Prompt</h3>
                            <p className="section-description">
                                Customize the AI's behavior. Leave empty to use the default legal AI prompt.
                            </p>

                            <div className="field-group">
                                <label>Your Custom Prompt</label>
                                <textarea
                                    className="prompt-textarea"
                                    value={customPrompt}
                                    onChange={(e) => setCustomPrompt(e.target.value)}
                                    placeholder="Enter your custom system prompt here...

Example: You are a literature expert. Answer questions about books, poetry, and literary analysis based on the provided context."
                                    rows={8}
                                />
                                <span className="char-count">{customPrompt.length} characters</span>
                            </div>

                            <div className="prompt-hint">
                                <strong>Tip:</strong> Your prompt will automatically include <code>{"{context}"}</code> and <code>{"{question}"}</code> placeholders if you don't add them.
                            </div>
                        </div>

                        {/* Message */}
                        {message.text && (
                            <div className={`settings-message ${message.type}`}>
                                {message.text}
                            </div>
                        )}

                        {/* Actions */}
                        <div className="settings-actions">
                            <button
                                className="reset-btn"
                                onClick={handleReset}
                                disabled={saving || !customPrompt}
                            >
                                <RotateCcw size={16} />
                                Reset to Default
                            </button>
                            <button
                                className="save-btn"
                                onClick={handleSave}
                                disabled={saving}
                            >
                                {saving ? <Loader2 className="animate-spin" size={16} /> : <Save size={16} />}
                                Save Changes
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Settings;
