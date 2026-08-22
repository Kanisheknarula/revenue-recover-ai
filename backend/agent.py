def choose_recovery_channel(recommended_action: str):
    if recommended_action == "send reminder":
        return "email"
    if recommended_action == "send discount offer":
        return "whatsapp"
    return "support_call"