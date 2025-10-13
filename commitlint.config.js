module.exports = {
    extends: [
        '@commitlint/config-conventional'
    ],
    rules: {
        // commit message 1st line of 150 characters max
        'header-max-length': [2, 'always', 150],
    }
}
