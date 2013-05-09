function towerToValue(tower, root) {
    return [
        {
            'col_value': $('<span class="state-' + tower.stateName +
                '"></span>'),
            'title_value': tower.stateName,
            'value': tower.state
        },
        tower.typeName,
        tower.regionName,
        tower.celestialName,
        tower.offlineAtFormatted,
        {
            'col_value': tower.timeRemainingFormatted,
            'value': tower.timeRemaining
        },
        {
            'col_value': $('<a href="' + root + tower.id + '">' +
                '<i class="icon-search"></i> details</a>'),
            'value': tower.id
        }
    ];
}
