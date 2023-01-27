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
    AdditionalSerializerConfig( # Lade Werke pro Kapitel
        url="additional/work_for_chapter",
        name="work_for_chapter",
        path_structure={
            Chapter: [
                Chapter.id,
                Chapter.name,
                Chapter.chapter_number,
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
                                    F1_Work.index_desc,                                
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
    AdditionalSerializerConfig( # Lade Details pro F21 Recording Work
        url="additional/f21_details",
        name="f21_details",
        path_structure={
            F21_Recording_Work: [
                F21_Recording_Work.id,
                F21_Recording_Work.name,
                F21_Recording_Work.genre,
                {
                    F21_Recording_Work.triple_set_from_subj: [
                        {
                            Triple.prop: [
                                Property.name,
                            ]
                        },
                        {
                            Triple.obj: [
                                    F31_Performance.id,                              
                                    F31_Performance.name,                              
                                    F31_Performance.start_date,
                                    F31_Performance.start_date_written,
                                    F31_Performance.note,
                                    F31_Performance.category,
                                    { 
                                        F31_Performance.triple_set_from_subj: [
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
                                        F31_Performance.triple_set_from_obj: [
                                            
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
                    F21_Recording_Work.triple_set_from_obj: [
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
                                    F31_Performance.note,
                                    F31_Performance.category,
                                    { 
                                        F31_Performance.triple_set_from_subj: [
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
                                        F31_Performance.triple_set_from_obj: [
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
                                    F31_Performance.id,                              
                                    F31_Performance.name,                              
                                    F31_Performance.start_date,
                                    F31_Performance.start_date_written,
                                    F31_Performance.note,
                                    F31_Performance.category,
                                    { 
                                        F31_Performance.triple_set_from_subj: [
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
                                        F31_Performance.triple_set_from_obj: [
                                            
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
                                    F31_Performance.note,
                                    F31_Performance.category,
                                    { 
                                        F31_Performance.triple_set_from_subj: [
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
                                        F31_Performance.triple_set_from_obj: [
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
    
    AdditionalSerializerConfig( # Lade Details pro Würdigung
        url="additional/honour_details",
        name="honour_details",
        path_structure={
            Honour: [
                Honour.id,
                Honour.name,
                {
                    Honour.triple_set_from_subj: [
                        {
                            Triple.prop: [
                                Property.name,
                            ]
                        },
                        {
                            Triple.obj: [
                                    F31_Performance.id,                              
                                    F31_Performance.name,                              
                                    F31_Performance.start_date,
                                    F31_Performance.start_date_written,
                                    F31_Performance.note,
                                    F31_Performance.category,
                                    { 
                                        F31_Performance.triple_set_from_subj: [
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
                                        F31_Performance.triple_set_from_obj: [
                                            
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
                    Honour.triple_set_from_obj: [
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
                                    F31_Performance.note,
                                    F31_Performance.category,
                                    { 
                                        F31_Performance.triple_set_from_subj: [
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
                                        F31_Performance.triple_set_from_obj: [
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
                                    F1_Work.index_desc,                                
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
                                                        F1_Work.index_desc,                                
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
                                                        F1_Work.index_desc,                                
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
                    F1_Work.index_desc,                                
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
                                    F1_Work.index_desc,                                
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
                    F1_Work.index_desc,                                
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
                                    F1_Work.index_desc,                                
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
    AdditionalSerializerConfig( # Lade nested triples for performance
        url="additional/nested_triples_to_performance",
        name="nested_triples_to_performance",
        path_structure={
            Triple: [
            {
                Triple.subj: [
                    E1_Crm_Entity.name,
                    E1_Crm_Entity.id,
                    F31_Performance.performance_id,
                    F31_Performance.short,
                    F31_Performance.start_date,
                    F31_Performance.start_date_written,
                    E1_Crm_Entity.self_content_type,
                    {
                        E1_Crm_Entity.triple_set_from_obj: [
                            {
                                Triple.subj: [
                                    F1_Work.name,
                                    F1_Work.short,
                                    F1_Work.id,
                                    F1_Work.index_in_chapter,                                
                                    F1_Work.index_desc,                                
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
                    F31_Performance.performance_id,
                    F31_Performance.short,
                    F31_Performance.start_date,
                    F31_Performance.start_date_written,
                    E1_Crm_Entity.self_content_type,
                    {
                        E1_Crm_Entity.triple_set_from_obj: [
                            {
                                Triple.subj: [
                                    F1_Work.name,
                                    F1_Work.short,
                                    F1_Work.id,
                                    F1_Work.index_in_chapter,                                
                                    F1_Work.index_desc,                                
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
    AdditionalSerializerConfig( # Lade Details pro Manifestation
        url="additional/manifestation_details",
        name="manifestation_details",
        path_structure={
            F3_Manifestation_Product_Type: [
                F3_Manifestation_Product_Type.id,
                F3_Manifestation_Product_Type.name,
                F3_Manifestation_Product_Type.start_date,
                F3_Manifestation_Product_Type.start_date_written,
                F3_Manifestation_Product_Type.note,
                F3_Manifestation_Product_Type.bibl_id,
                F3_Manifestation_Product_Type.series,
                F3_Manifestation_Product_Type.edition,
                F3_Manifestation_Product_Type.page,
                F3_Manifestation_Product_Type.issue,
                F3_Manifestation_Product_Type.volume,
                F3_Manifestation_Product_Type.ref_target,
                F3_Manifestation_Product_Type.ref_accessed,
                F3_Manifestation_Product_Type.text_language,
                F3_Manifestation_Product_Type.short,
                F3_Manifestation_Product_Type.untertitel,
                F3_Manifestation_Product_Type.scope_style,
                F3_Manifestation_Product_Type.self_content_type,
                {
                    F3_Manifestation_Product_Type.triple_set_from_subj: [
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
                                    F3_Manifestation_Product_Type.note,
                                    F3_Manifestation_Product_Type.bibl_id,
                                    F3_Manifestation_Product_Type.series,
                                    F3_Manifestation_Product_Type.edition,
                                    F3_Manifestation_Product_Type.page,
                                    F3_Manifestation_Product_Type.issue,
                                    F3_Manifestation_Product_Type.volume,
                                    F3_Manifestation_Product_Type.ref_target,
                                    F3_Manifestation_Product_Type.ref_accessed,
                                    F3_Manifestation_Product_Type.text_language,
                                    F3_Manifestation_Product_Type.short,
                                    F3_Manifestation_Product_Type.untertitel,
                                    F3_Manifestation_Product_Type.scope_style,
                                    F3_Manifestation_Product_Type.self_content_type,
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
                                    F3_Manifestation_Product_Type.id,
                                    F3_Manifestation_Product_Type.name,
                                    F3_Manifestation_Product_Type.start_date,
                                    F3_Manifestation_Product_Type.start_date_written,
                                    F3_Manifestation_Product_Type.note,
                                    F3_Manifestation_Product_Type.bibl_id,
                                    F3_Manifestation_Product_Type.series,
                                    F3_Manifestation_Product_Type.edition,
                                    F3_Manifestation_Product_Type.page,
                                    F3_Manifestation_Product_Type.issue,
                                    F3_Manifestation_Product_Type.volume,
                                    F3_Manifestation_Product_Type.ref_target,
                                    F3_Manifestation_Product_Type.ref_accessed,
                                    F3_Manifestation_Product_Type.text_language,
                                    F3_Manifestation_Product_Type.short,
                                    F3_Manifestation_Product_Type.untertitel,
                                    F3_Manifestation_Product_Type.scope_style,
                                    F3_Manifestation_Product_Type.self_content_type,
                            ]
                        },
                        
                    ]
                }
            ]
        }
    ),
    AdditionalSerializerConfig( # Lade Notes
        url="additional/notes",
        name="note_details",
        path_structure={
            XMLNote: [
                XMLNote.id,
                XMLNote.content,
                XMLNote.rendition,
                XMLNote.type,
                {
                    XMLNote.triple_set_from_obj: [
                        {
                            Triple.prop: [
                                Property.name
                            ]
                        },
                        {
                            Triple.subj: [
                                    TempEntityClass.id,                              
                                    TempEntityClass.name,                              
                            ]
                        },
                        
                    ]
                }
            ]            
        }
    ),
    AdditionalSerializerConfig( # Simple Triple List
        url="additional/triples",
        name="triples",
        path_structure={
            Triple: [
                {
                    Triple.subj: [
                        E1_Crm_Entity.name,
                        E1_Crm_Entity.id,
                        E1_Crm_Entity.self_content_type,
                    ]
                },
                {
                    Triple.prop: [
                        Property.name,
                    ]
                },
                {
                    Triple.obj: [
                        E1_Crm_Entity.name,
                        E1_Crm_Entity.id,
                        E1_Crm_Entity.self_content_type,
                    ]
                }
            ]
        }
    ),
    AdditionalSerializerConfig( # Triples for filters (date, language,)
        url="additional/search_filter_triples",
        name="search_filter_triples",
        path_structure={
            Triple: [
                {
                    Triple.subj: [
                        E1_Crm_Entity.name,
                        E1_Crm_Entity.id,
                        E1_Crm_Entity.self_content_type,
                        {
                            E1_Crm_Entity.triple_set_from_obj: [
                                {
                                    Triple.subj: [
                                        E1_Crm_Entity.name,
                                        E1_Crm_Entity.self_content_type
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
                        Property.name,
                    ]
                },
                {
                    Triple.obj: [
                        E1_Crm_Entity.name,
                        E1_Crm_Entity.id,
                        E1_Crm_Entity.self_content_type,
                        E1_Crm_Entity.start_date,
                        E1_Crm_Entity.start_date_written,
                        F3_Manifestation_Product_Type.text_language,
                         {
                            E1_Crm_Entity.triple_set_from_subj: [
                                {
                                    Triple.obj: [
                                        E1_Crm_Entity.name,
                                        E1_Crm_Entity.self_content_type
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
                }
            ]
        }
    ),

]
