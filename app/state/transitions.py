from app.enums import BotState


ALLOWED: dict[BotState, set[BotState]] = {
    BotState.IDLE: {BotState.SCAN},
    BotState.SCAN: {BotState.NO_TRADE, BotState.ARMED, BotState.DAILY_LOCK},
    BotState.NO_TRADE: {BotState.SCAN, BotState.COOLDOWN},
    BotState.ARMED: {BotState.ENTRY_PENDING, BotState.NO_TRADE},
    BotState.ENTRY_PENDING: {BotState.POSITION_OPEN, BotState.NO_TRADE},
    BotState.POSITION_OPEN: {BotState.MANAGE, BotState.ADDON_READY, BotState.COOLDOWN},
    BotState.MANAGE: {BotState.ADDON_READY, BotState.COOLDOWN, BotState.DAILY_LOCK},
    BotState.ADDON_READY: {BotState.MANAGE, BotState.COOLDOWN},
    BotState.COOLDOWN: {BotState.SCAN, BotState.DAILY_LOCK},
    BotState.DAILY_LOCK: {BotState.IDLE},
    BotState.RECOVERY: {BotState.SCAN, BotState.DAILY_LOCK},
    BotState.AXX_PRIME_USED: {BotState.SCAN, BotState.COOLDOWN},
}
