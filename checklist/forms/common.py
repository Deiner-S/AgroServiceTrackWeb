INPUT_TW_CLASS = (
    "w-full px-4 py-3 bg-gray-700 border border-gray-500 rounded-xl shadow-sm "
    "text-white placeholder-gray-300 "
    "focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-gray-400 "
    "transition-all duration-200"
)

LOCKED_INPUT_TW_CLASS = (
    "w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-xl shadow-sm "
    "text-gray-300 cursor-not-allowed select-none opacity-100 "
    "focus:outline-none focus:ring-0 focus:border-gray-200"
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
