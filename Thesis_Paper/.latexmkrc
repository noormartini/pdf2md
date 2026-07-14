# Run makeglossaries so the List of Abbreviations is built (glossaries package).
add_cus_dep('glo', 'gls', 0, 'run_makeglossaries');
add_cus_dep('acn', 'acr', 0, 'run_makeglossaries');
sub run_makeglossaries {
    return system("makeglossaries \"$_[0]\"");
}
push @generated_exts, 'glo', 'gls', 'glg', 'acn', 'acr', 'alg';
