from dataclasses import dataclass
from apis_ontology.models import *
from apis_core.apis_relations.models import *
from apis_core.apis_metainfo.models import *

@dataclass
class AdditionalSerializerConfig:
    url: str # For now, it is recommended to prefix the url with 'additional'
    name: str # unique name for django
    path_structure: dict # see example structure
    viewset = None # will be programmatically generated

additional_serializers_list = [
    AdditionalSerializerConfig( # Keep this example one for now
        url="additional/example_serializer",
        name="some_example_serializer",
        path_structure={
            F1_Work: [
                F1_Work.id,
                F1_Work.name,
                F1_Work.idno,
                {
                    F1_Work.triple_set_from_subj: [
                        {
                            Triple.prop: [
                                Property.name_forward,
                                Property.name_reverse,
                            ]
                        },
                        {
                            Triple.obj: [
                                F3_Manifestation_Product_Type.name,
                                F3_Manifestation_Product_Type.bibl_id,
                                {
                                    F3_Manifestation_Product_Type.triple_set_from_obj: [
                                        {
                                            Triple.prop: [
                                                Property.name_forward,
                                                Property.name_reverse,
                                            ]
                                        },
                                        {
                                            Triple.subj: [
                                                F10_Person.name
                                            ],
                                        }
                                    ]
                                }
                            ]
                        },
                    ]
                },
            ]
        }
    ),
    AdditionalSerializerConfig( # fuer Gregor zum vergleichen, wird bald wieder geloescht
        url="additional/example_serializer_2",
        name="some_example_serializer_2",
        path_structure={
            F1_Work: [
                F1_Work.id,
                F1_Work.name,
                F1_Work.idno,
                {
                    F1_Work.triple_set_from_subj: [
                        Triple.subj,
                        Triple.obj,
                        {
                            Triple.prop: [
                                Property.name,
                                {
                                    Property.subj_class: [
                                        ContentType.model
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ),
    AdditionalSerializerConfig( # Lade Werke pro Kapitel
        url="additional/work_for_chapter",
        name="work_for_chapter",
        path_structure={
            Chapter: [
                Chapter.id,
                Chapter.name,
                {
                    Chapter.triple_set_from_obj: [
                        {
                            Triple.prop: [
                                Property.name
                            ]
                        },
                        {
                            Triple.subj: [
                                    F1_Work.name,
                                    F1_Work.short,
                                    F1_Work.id,
                                    F1_Work.index_in_chapter,                                
                                    F1_Work.idno,                                
                                    F1_Work.genre,                                
                            ]
                        },
                        
                    ]
                }
            ]            
        }
    ),
    AdditionalSerializerConfig( # Lade Kapitel für Werk
        url="additional/work_chapters",
        name="work_chapters",
        path_structure={
            F1_Work: [
                F1_Work.id,
                F1_Work.name,
                {
                    F1_Work.triple_set_from_subj: [
                        {
                            Triple.prop: [
                                Property.name,
                            ]
                        },
                        {
                            Triple.obj: [
                                    Chapter.id,                              
                                    Chapter.name,                              
                                    Chapter.chapter_number
                            ]
                        },
                        
                    ]
                }
            ]            
        }
    ),
    AdditionalSerializerConfig( # Lade Details pro Werk
        url="additional/work_details",
        name="work_details",
        path_structure={
            F1_Work: [
                F1_Work.id,
                F1_Work.name,
                F1_Work.genre,
                {
                    F1_Work.triple_set_from_subj: [
                        {
                            Triple.prop: [
                                Property.name,
                            ]
                        },
                        {
                            Triple.obj: [
                                    F3_Manifestation_Product_Type.id,                              
                                    F3_Manifestation_Product_Type.name,                              
                                    F3_Manifestation_Product_Type.start_date,
                                    F3_Manifestation_Product_Type.start_date_written,
                                    F3_Manifestation_Product_Type.edition,
                                    F3_Manifestation_Product_Type.bibl_id,
                                    { 
                                        F3_Manifestation_Product_Type.triple_set_from_subj: [
                                            {
                                                Triple.prop: [
                                                    Property.name,
                                                ]
                                            },
                                            {
                                                Triple.obj: [
                                                        TempEntityClass.id,
                                                        TempEntityClass.name
                                                ]
                                            },
                                        ]
                                    },
                                    { 
                                        F3_Manifestation_Product_Type.triple_set_from_obj: [
                                            
                                            {
                                                Triple.prop: [
                                                    Property.name,
                                                ]
                                            },
                                            {
                                                Triple.subj: [
                                                        TempEntityClass.id,
                                                        TempEntityClass.name
                                                ]
                                            },
                                        ]
                                    }
                            ]
                        },
                        
                    ]
                },
                {
                    F1_Work.triple_set_from_obj: [
                        {
                            Triple.prop: [
                                Property.name,
                            ]
                        },
                        {
                            Triple.subj: [
                                    TempEntityClass.id,                              
                                    TempEntityClass.name,                              
                                    TempEntityClass.start_date,
                                    TempEntityClass.start_date_written,
                                    F3_Manifestation_Product_Type.edition,
                                    F3_Manifestation_Product_Type.bibl_id,
                                    { 
                                        F3_Manifestation_Product_Type.triple_set_from_subj: [
                                            {
                                                Triple.prop: [
                                                    Property.name,
                                                ]
                                            },
                                            
                                            {
                                                Triple.obj: [
                                                        TempEntityClass.id,
                                                        TempEntityClass.name
                                                ]
                                            },
                                        ]
                                    },
                                    { 
                                        F3_Manifestation_Product_Type.triple_set_from_obj: [
                                            {
                                                Triple.prop: [
                                                    Property.name,
                                                ]
                                            },
                                            {
                                                Triple.subj: [
                                                        TempEntityClass.id,
                                                        TempEntityClass.name
                                                ]
                                            },
                                        ]
                                    }
                            ]
                        },
                        
                    ]
                }
            ]            
        }
    ),
    AdditionalSerializerConfig( # Lade Werke pro Keyword
        url="additional/work_for_keyword",
        name="work_for_keyword",
        path_structure={
            Keyword: [
                Keyword.id,
                Keyword.name,
                {
                    Keyword.triple_set_from_obj: [
                        {
                            Triple.prop: [
                                Property.name
                            ]
                        },
                        {
                            Triple.subj: [
                                    F1_Work.name,
                                    F1_Work.short,
                                    F1_Work.id,
                                    F1_Work.index_in_chapter,                                
                                    F1_Work.idno,                                
                                    F1_Work.genre,                                
                            ]
                        },
                        
                    ]
                }
            ]            
        }
    ),
    AdditionalSerializerConfig( # Lade Werke pro Institution
        url="additional/work_for_institution",
        name="work_for_institution",
        path_structure={
            E40_Legal_Body: [
                E40_Legal_Body.id,
                E40_Legal_Body.name,
                {
                    E40_Legal_Body.triple_set_from_obj: [
                        {
                            Triple.prop: [
                                Property.name
                            ]
                        },
                        {
                            Triple.subj: [
                                    F31_Performance.name,                             
                                    F31_Performance.id,  
                                    {
                                        F31_Performance.triple_set_from_obj: [
                                            {
                                                Triple.prop: [
                                                    Property.name
                                                ]
                                            },
                                            {
                                                Triple.subj: [
                                                        F1_Work.name,
                                                        F1_Work.short,
                                                        F1_Work.id,
                                                        F1_Work.index_in_chapter,                                
                                                        F1_Work.idno,                                
                                                        F1_Work.genre,                             
                                                ]
                                            },
                                            
                                        ]
                                    }                           
                            ]
                        },
                        
                    ]
                },
                {
                    E40_Legal_Body.triple_set_from_subj: [
                        {
                            Triple.prop: [
                                Property.name
                            ]
                        },
                        {
                            Triple.obj: [
                                    F31_Performance.name,                             
                                    F31_Performance.id,  
                                    {
                                        F31_Performance.triple_set_from_obj: [
                                            {
                                                Triple.prop: [
                                                    Property.name
                                                ]
                                            },
                                            {
                                                Triple.subj: [
                                                        F1_Work.name,
                                                        F1_Work.short,
                                                        F1_Work.id,
                                                        F1_Work.index_in_chapter,                                
                                                        F1_Work.idno,                                
                                                        F1_Work.genre,                             
                                                ]
                                            },
                                            
                                        ]
                                    }                           
                            ]
                        },
                        
                    ]
                }
            ]            
        }
    ),
    AdditionalSerializerConfig( # Lade nested triples
        url="additional/nested_triples_to_work",
        name="nested_triples",
        path_structure={
            Triple: [
            {
                Triple.subj: [
                    E1_Crm_Entity.name,
                    E1_Crm_Entity.id,
                    F1_Work.short,
                    F1_Work.index_in_chapter,                                
                    F1_Work.idno,                                
                    F1_Work.genre,
                    E1_Crm_Entity.self_content_type,
                    {
                        E1_Crm_Entity.triple_set_from_obj: [
                            {
                                Triple.subj: [
                                    F1_Work.name,
                                    F1_Work.short,
                                    F1_Work.id,
                                    F1_Work.index_in_chapter,                                
                                    F1_Work.idno,                                
                                    F1_Work.genre,
                                    F1_Work.self_content_type
                                ]
                            },
                            {
                                Triple.prop: [
                                    Property.name
                                ]
                            },
                        ]
                    },
                ]
            },
            {
                Triple.prop: [
                    Property.name
                ]
            },
            {
                Triple.obj: [
                    E1_Crm_Entity.name,
                    E1_Crm_Entity.id,
                    F1_Work.short,
                    F1_Work.index_in_chapter,                                
                    F1_Work.idno,                                
                    F1_Work.genre,
                    E1_Crm_Entity.self_content_type,
                    {
                        E1_Crm_Entity.triple_set_from_obj: [
                            {
                                Triple.subj: [
                                    F1_Work.name,
                                    F1_Work.short,
                                    F1_Work.id,
                                    F1_Work.index_in_chapter,                                
                                    F1_Work.idno,                                
                                    F1_Work.genre,
                                    F1_Work.self_content_type
                                ]
                            },
                            {
                                Triple.prop: [
                                    Property.name
                                ]
                            },
                        ]
                    },
                ]
            },
            ]
        }
    ),
]
