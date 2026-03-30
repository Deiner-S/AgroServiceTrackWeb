INPUT_TW_CLASS = (
    "w-full rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3.5 "
    "text-slate-100 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)] backdrop-blur-sm "
    "placeholder:text-slate-400 "
    "focus:border-sky-300/40 focus:outline-none focus:ring-4 focus:ring-sky-400/10 "
    "transition-all duration-200"
)

LOCKED_INPUT_TW_CLASS = (
    "w-full rounded-2xl border border-white/8 bg-slate-950/80 px-4 py-3.5 "
    "text-slate-400 cursor-not-allowed select-none opacity-100 "
    "focus:border-white/8 focus:outline-none focus:ring-0"
)

CPF_INPUT_ATTRS = {
    "data-mask": "cpf",
    "inputmode": "numeric",
    "maxlength": "14",
    "autocomplete": "off",
}

PHONE_INPUT_ATTRS = {
    "data-mask": "phone",
    "inputmode": "numeric",
    "maxlength": "15",
    "autocomplete": "off",
}

ZIP_CODE_INPUT_ATTRS = {
    "data-mask": "zip_code",
    "inputmode": "numeric",
    "maxlength": "9",
    "autocomplete": "off",
}
