---------------------------
--       emergency       --
---------------------------
INSERT INTO osmaxx.poi_p
 SELECT osm_id as osm_id,
	osm_timestamp as lastchange,
	'N' AS geomtype, 	-- Node
	way AS geom,
-- Combining the different tags in Emergency into different categories --
	case
	 when emergency in ('phone','fire_hydrant') then 'miscpoi'
	end as aggtype,
	case
	 when emergency='phone' then 'emergency_phone'
	 when emergency='fire_hydrant' then 'fire_hydrant'
	end as type,
	name as name,
	"name:en" as name_en,
	"name:fr" as name_fr,
	"name:es" as name_es,
	"name:de" as name_de,
	int_name as name_int,
	case
		when name is not null AND name = transliterate(name) then name
		when name_en is not null then name_en
		when name_fr is not null then name_fr
		when name_es is not null then name_es
		when name_de is not null then name_de
		when name is not null then transliterate(name)
		else NULL
	end as label, 
	#transliterate(name) as label,
	cast(tags as text) as tags,
	website as website,
	wikipedia as wikipedia,
	phone as phone,
	"contact:phone" as contact_phone,
	opening_hours as opening_hours,
	cuisine as cuisine,
	"access" as "access",
	brand as brand,
	"tower:type" as tower_type
  FROM osm_point
  WHERE emergency in ('phone','fire_hydrant')
UNION
 SELECT osm_id as osm_id,
	osm_timestamp as lastchange,
	CASE
	 WHEN osm_id<0 THEN 'R' -- Relation
	 ELSE 'W' 		-- Way
	 END AS geomtype,
	ST_Centroid(way) AS geom,
-- Combining the different tags in Emergency into different categories --
	case
	 when emergency in ('phone','fire_hydrant') then 'miscpoi'
	end as aggtype,
	case
	 when emergency='phone' then 'emergency_phone'
	 when emergency='fire_hydrant' then 'fire_hydrant'
	end as type,

	name as name,
	"name:en" as name_en,
	"name:fr" as name_fr,
	"name:es" as name_es,
	"name:de" as name_de,
	int_name as name_int,
	case
		when name is not null AND name = transliterate(name) then name
		when name_en is not null then name_en
		when name_fr is not null then name_fr
		when name_es is not null then name_es
		when name_de is not null then name_de
		when name is not null then transliterate(name)
		else NULL
	end as label, 
	#transliterate(name) as label,
	cast(tags as text) as tags,
	website as website,
	wikipedia as wikipedia,
	phone as phone,
	"contact:phone" as contact_phone,
	opening_hours as opening_hours,
	cuisine as cuisine,
	"access" as "access",
	brand as brand,
	"tower:type" as tower_type
  FROM osm_polygon
  WHERE emergency in ('phone','fire_hydrant');
