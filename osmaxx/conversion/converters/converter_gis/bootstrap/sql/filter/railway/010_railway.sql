/*key:railway*/
INSERT INTO osmaxx.railway_l
  SELECT osm_id as osm_id,
    osm_timestamp as lastchange ,
    'W' AS geomtype,     -- Way
    ST_Multi(way) AS geom,
    'railway' as aggtype,
-- Combining different tags for Railway --
    case
    when railway in ('rail','light_rail','subway','tram','monorail','narrow_gauge','miniature','funicular','rack') then railway
    else 'railway'
    end as type,

    name as name,
    "name:en" as name_en,
    "name:fr" as name_fr,
    "name:es" as name_es,
    "name:de" as name_de,
    int_name as name_int,
    case
        when name is not null AND name = transliterate(name) then name
        when "name:en" is not null then "name:en"
        when "name:fr" is not null then "name:fr"
        when "name:es" is not null then "name:es"
        when "name:de" is not null then "name:de"
        when name is not null then transliterate(name)
        else NULL
    end as label,
    cast(tags as text) as tags,
    z_order as z_order,
-- Combining different tags for Bridges --
    case
    when bridge in ('split_log' , 'beam', 'culvert', 'low_water_crossing', 'yes', 'suspension', 'viaduct', 'aqueduct', 'covered') then TRUE
    else FALSE
    end as bridge,
-- Combining different tags for Tunnels --
    case
    when tunnel in ('passage', 'culvert', 'noiseprotection galerie', 'gallery', 'building_passage', 'avalanche_protector','teilweise', 'viaduct', 'tunnel', 'yes') then TRUE
    else FALSE
    end as tunnel,
    voltage as voltage,
    frequency as frequency
     FROM osm_line
     WHERE railway not in ('abandon','construction','disused','planned');
