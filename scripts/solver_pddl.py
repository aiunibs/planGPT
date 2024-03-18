from tqdm import tqdm
from transformers import AutoTokenizer
import transformers
import os
import sys
transformers.logging.set_verbosity_error()
import json
from model import GPT2PModel
import re
import random
import time
import metric
from parse_problem import *
import logging
from transformers import HfArgumentParser
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import time
import copy
random.seed(42)

@dataclass
class SolvingPDDLArgs:
    """
    Opzioni per la costruzione di un piano in formato JSON.
    """
    domain:str = field(
        default="satellite",
        metadata={"help": "Dominio del dataset"},
    )
    pddl_dir:str = field(
        default="../pddl/satellite_2/",
        metadata={"help": "Directory in cui sono contenuti i json"},
    )
    output_dir:str = field(
        default="../new_datasets/satellite/with_invariants_and_types_random_multiply/",
        metadata={"help": "Directory in cui salveremo i file generati"},
    )
    model_dir:str = field(
        default="../training_sorted/random_new_eval_satellite_with_invariants_and_types",
        metadata={"help": "Directory in cui è contenuto il modello"},
    )
    tokenizer_dir:str = field(
        default="../training_sorted/random_new_eval_satellite_with_invariants_and_types",
        metadata={"help": "Directory in cui è contenuto il tokenizer"},
    )
    randomize:bool = field(
        default=True,
        metadata={"help": "Randomizza gli oggetti"},
    )
    typed_domain:bool = field(
        default=True,
        metadata={"help": "Dominio tipizzato"},
    )
    # Parametri di generazione 
    max_length: Optional[int] = field(
        default=2048,
        metadata={"help": "Lunghezza massima dei piani"},
    )
    sorted_assignment: Optional[bool] = field(
        default=False,
        metadata={"help": "Per indicare se è da usare l'ordinamento nell'assegnazione degli oggetti"},
    )
    num_beams: Optional[int] = field(
        default=1, metadata={"help": "Per indicare se è da usare la beam search"})
    top_k: Optional[int] = field(
        default=50, metadata={"help": "Per indicare se è da usare top-k"})
    top_p: Optional[float] = field(
        default=1.0, metadata={"help": "Per indicare se è da usare top-p"})
    do_sample: Optional[bool] = field(
        default=False, metadata={"help": "Per indicare se è da usare il sampling"})

    num_return_sequences: Optional[int] = field(
        default=1, metadata={"help": "Per indicare se è da usare la beam search"})
    log_file_name: Optional[str] = field(
        default="generation.log", metadata={"help": "Nome del file di log."}
    )
logger = logging.getLogger(__name__)

types_identifiers = {
    "blocksworld": ["block"],
    "childsnack": [],
    "logistics": ["package", "airplane", "airport", "city", "location", "truck"],
    "zenotravel": ["aircraft", "city", "person", "flevel"],
    "depots": ["depot", "truck", "distributor", "hoist", "crate", "pallet"],
    "satellite": ["satellite", "instrument", "direction", "mode"],
    "driverlog": ["truck", "location", "obj", "driver"],
    "sokoban": ["dir", "box", "loc"],
    "floortile": ["tile", "robot", "color"],
    "visitall" : ["place"],
}

objects_from_tokenizer = {
    "zenotravel": 
        {
            "aircraft": ["plane1","plane2", "plane3", "plane4", "plane5"],
            # fino a 20 person
            "person": ["person1", "person2", "person3", "person4", "person5", "person6", "person7", "person8", "person9", "person10", "person11", "person12", "person13", "person14", "person15", "person16", "person17", "person18", "person19", "person20"],
            # Fino a 17 city
            "city": ["city0", "city1", "city2", "city3", "city4", "city5", "city6", "city7", "city8", "city9", "city10", "city11", "city12", "city13", "city14", "city15", "city16", "city17"],
            "flevel": ["fl0", "fl1", "fl2", "fl3", "fl4", "fl5", "fl6"],
        },
    "depots":
        {
            "depot": ["depot0", "depot1", "depot2", "depot3", "depot4", "depot5"],
            "truck": ["truck0", "truck1", "truck2", "truck3", "truck4", "truck5"],
            "distributor": ["distributor0", "distributor1", "distributor2", "distributor3", "distributor4", "distributor5"],
            "hoist": ["hoist0", "hoist1", "hoist2", "hoist3", "hoist4", "hoist5", "hoist6", "hoist7", "hoist8", "hoist9", "hoist10", "hoist11", "hoist12", "hoist13", "hoist14"],
            "crate": ["crate0", "crate1", "crate2", "crate3", "crate4", "crate5", "crate6", "crate7", "crate8", "crate9", "crate10", "crate11", "crate12", "crate13", "crate14"],
            "pallet": ["pallet0", "pallet1", "pallet2", "pallet3", "pallet4", "pallet5", "pallet6", "pallet7", "pallet8", "pallet9", "pallet10", "pallet11", "pallet12", "pallet13", "pallet14"],
        },
    "satellite":
        {   
            # satellite da 1 a 10

            "satellite": ["satellite1", "satellite2", "satellite3", "satellite4", "satellite5", "satellite6", "satellite7", "satellite8", "satellite9", "satellite10" ],
            # Fino a 28 strumenti
            "instrument": ["instrument1", "instrument2", "instrument3", "instrument4", "instrument5", "instrument6", "instrument7", "instrument8", "instrument9","instrument10", "instrument11", "instrument12", "instrument13",
                "instrument14", "instrument15", "instrument16", "instrument17", "instrument18", "instrument19","instrument20", "instrument21", "instrument22", "instrument23", "instrument24", "instrument25", "instrument26", "instrument27", "instrument28", "instrument29"],
            # direction da 1 a 45
            "direction": ["direction1", "direction2", "direction3", "direction4", "direction5", "direction6", "direction7", "direction8", "direction9", "direction10", "direction11", "direction12", "direction13", "direction14", "direction15", "direction16", "direction17", "direction18", "direction19", "direction20", "direction21", "direction22", "direction23", "direction24", "direction25", "direction26", "direction27", "direction28", "direction29", "direction30", "direction31", "direction32", "direction33", "direction34", "direction35", "direction36", "direction37", "direction38", "direction39", "direction40", "direction41", "direction42", "direction43", "direction44", "direction45"],
            "mode":["mode1", "mode2", "mode3", "mode4", "mode5"],
        },
    "blocksworld":
        {
            # Da b1 fino a b30
            #"block" : ["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8","b9", "b10", "b11", "b12", "b13", "b14", "b15", "b16","b17", "b18", "b19", "b20", "b21", "b22", "b23", "b24","b25", "b26", "b27", "b28", "b29", "b30"],
            "block" : ["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8","b9", "b10", "b11", "b12", "b13", "b14", "b15", "b16","b17", "b18", "b19", "b20"],
        },
    "driverlog":
        {
            # Newer
            # da truck1 a truck5
            "truck": ["truck1", "truck2", "truck3", "truck4", "truck5", "truck6"],
            "driver": ["driver1", "driver2", "driver3", "driver4", "driver5", "driver6", "driver7", "driver8"],
            #package1 a 20
            "obj": ["package1", "package2", "package3", "package4", "package5", "package6", "package7", "package8", "package9", "package10", "package11", "package12", "package13", "package14", "package15", "package16", "package17", "package18", "package19", "package20", "package21", "package22", "package23", "package24", "package25"],
            # p da 0 a 20
            # s fino a 19
            # P fino a 380
            "location": ["s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7","s8", "s9", "s10", "s11", "s12", "s13", "s14", "s15","s16", "s17", "s18", "s19","p0", "p1", "p10", "p100", "p101", "p102", "p103", "p104", "p105", "p106", "p107", "p108", "p109", "p11", "p110", "p111", "p112", "p113", "p114", "p115", "p116", "p117", "p118", "p119", "p12", "p120", "p121", "p122", "p123", "p124", "p125", "p126", "p127", "p128", "p129", "p13", "p130", "p131", "p132", "p133", "p134", "p135", "p136", "p137", "p138", "p139", "p14", "p140", "p141", "p142", "p143", "p144", "p145", "p146", "p147", "p148", "p149", "p15", "p150", "p151", "p152", "p153", "p154", "p155", "p156", "p157", "p158", "p159", "p16", "p160", "p161", "p162", "p163", "p164", "p165", "p166", "p167", "p168", "p169", "p17", "p170", "p171", "p172", "p173", "p174", "p175", "p176", "p177", "p178", "p179", "p18", "p180", "p181", "p182", "p183", "p184", "p185", "p186", "p187", "p188", "p189", "p19", "p190", "p191", "p192", "p193", "p194", "p195", "p196", "p197", "p198", "p199", "p2", "p20", "p200", "p201", "p202", "p203", "p204", "p205", "p206", "p207", "p208", "p209", "p21", "p210", "p211", "p212", "p213", "p214", "p215", "p216", "p217", "p218", "p219", "p22", "p220", "p221", "p222", "p223", "p224", "p225", "p226", "p227", "p228", "p229", "p23", "p230", "p231", "p232", "p233", "p234", "p235", "p236", "p237", "p238", "p239", "p24", "p240", "p241", "p242", "p243", "p244", "p245", "p246", "p247", "p248", "p249", "p25", "p250", "p251", "p252", "p253", "p254", "p255", "p256", "p257", "p258", "p259", "p26", "p260", "p261", "p262", "p263", "p264", "p265", "p266", "p267", "p268", "p269", "p27", "p270", "p271", "p272", "p273", "p274", "p275", "p276", "p277", "p278", "p279", "p28", "p280", "p281", "p282", "p283", "p284", "p285", "p286", "p287", "p288", "p289", "p29", "p290", "p291", "p292", "p293", "p294", "p295", "p296", "p297", "p298", "p299", "p3", "p30", "p300", "p301", "p302", "p303", "p304", "p305", "p306", "p307", "p308", "p309", "p31", "p310", "p311", "p312", "p313", "p314", "p315", "p316", "p317", "p318", "p319", "p32", "p320", "p321", "p322", "p323", "p324", "p325", "p326", "p327", "p328", "p329", "p33", "p330", "p331", "p332", "p333", "p334", "p335", "p336", "p337", "p338", "p339", "p34", "p340", "p341", "p342", "p343", "p344", "p345", "p346", "p347", "p348", "p349", "p35", "p350", "p351", "p352", "p353", "p354", "p355", "p356", "p357", "p358", "p359", "p36", "p360", "p361", "p362", "p363", "p364", "p365", "p366", "p367", "p368", "p369", "p37", "p370", "p371", "p372", "p373", "p374", "p375", "p376", "p377", "p378", "p379", "p38", "p380", "p39", "p4", "p40", "p41", "p42", "p43", "p44", "p45", "p46", "p47", "p48", "p49", "p5", "p50", "p51", "p52", "p53", "p54", "p55", "p56", "p57", "p58", "p59", "p6", "p60", "p61", "p62", "p63", "p64", "p65", "p66", "p67", "p68", "p69", "p7", "p70", "p71", "p72", "p73", "p74", "p75", "p76", "p77", "p78", "p79", "p8", "p80", "p81", "p82", "p83", "p84", "p85", "p86", "p87", "p88", "p89", "p9", "p90", "p91", "p92", "p93", "p94", "p95", "p96", "p97", "p98", "p99"],
            "p_location": ["p0", "p1", "p10", "p100", "p101", "p102", "p103", "p104", "p105", "p106", "p107", "p108", "p109", "p11", "p110", "p111", "p112", "p113", "p114", "p115", "p116", "p117", "p118", "p119", "p12", "p120", "p121", "p122", "p123", "p124", "p125", "p126", "p127", "p128", "p129", "p13", "p130", "p131", "p132", "p133", "p134", "p135", "p136", "p137", "p138", "p139", "p14", "p140", "p141", "p142", "p143", "p144", "p145", "p146", "p147", "p148", "p149", "p15", "p150", "p151", "p152", "p153", "p154", "p155", "p156", "p157", "p158", "p159", "p16", "p160", "p161", "p162", "p163", "p164", "p165", "p166", "p167", "p168", "p169", "p17", "p170", "p171", "p172", "p173", "p174", "p175", "p176", "p177", "p178", "p179", "p18", "p180", "p181", "p182", "p183", "p184", "p185", "p186", "p187", "p188", "p189", "p19", "p190", "p191", "p192", "p193", "p194", "p195", "p196", "p197", "p198", "p199", "p2", "p20", "p200", "p201", "p202", "p203", "p204", "p205", "p206", "p207", "p208", "p209", "p21", "p210", "p211", "p212", "p213", "p214", "p215", "p216", "p217", "p218", "p219", "p22", "p220", "p221", "p222", "p223", "p224", "p225", "p226", "p227", "p228", "p229", "p23", "p230", "p231", "p232", "p233", "p234", "p235", "p236", "p237", "p238", "p239", "p24", "p240", "p241", "p242", "p243", "p244", "p245", "p246", "p247", "p248", "p249", "p25", "p250", "p251", "p252", "p253", "p254", "p255", "p256", "p257", "p258", "p259", "p26", "p260", "p261", "p262", "p263", "p264", "p265", "p266", "p267", "p268", "p269", "p27", "p270", "p271", "p272", "p273", "p274", "p275", "p276", "p277", "p278", "p279", "p28", "p280", "p281", "p282", "p283", "p284", "p285", "p286", "p287", "p288", "p289", "p29", "p290", "p291", "p292", "p293", "p294", "p295", "p296", "p297", "p298", "p299", "p3", "p30", "p300", "p301", "p302", "p303", "p304", "p305", "p306", "p307", "p308", "p309", "p31", "p310", "p311", "p312", "p313", "p314", "p315", "p316", "p317", "p318", "p319", "p32", "p320", "p321", "p322", "p323", "p324", "p325", "p326", "p327", "p328", "p329", "p33", "p330", "p331", "p332", "p333", "p334", "p335", "p336", "p337", "p338", "p339", "p34", "p340", "p341", "p342", "p343", "p344", "p345", "p346", "p347", "p348", "p349", "p35", "p350", "p351", "p352", "p353", "p354", "p355", "p356", "p357", "p358", "p359", "p36", "p360", "p361", "p362", "p363", "p364", "p365", "p366", "p367", "p368", "p369", "p37", "p370", "p371", "p372", "p373", "p374", "p375", "p376", "p377", "p378", "p379", "p38", "p380", "p39", "p4", "p40", "p41", "p42", "p43", "p44", "p45", "p46", "p47", "p48", "p49", "p5", "p50", "p51", "p52", "p53", "p54", "p55", "p56", "p57", "p58", "p59", "p6", "p60", "p61", "p62", "p63", "p64", "p65", "p66", "p67", "p68", "p69", "p7", "p70", "p71", "p72", "p73", "p74", "p75", "p76", "p77", "p78", "p79", "p8", "p80", "p81", "p82", "p83", "p84", "p85", "p86", "p87", "p88", "p89", "p9", "p90", "p91", "p92", "p93", "p94", "p95", "p96", "p97", "p98", "p99", ], 
                        # p da 0 a 20
            "s_location": ["s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7","s8", "s9", "s10", "s11", "s12", "s13", "s14", "s15","s16", "s17", "s18", "s19",],
            
            #OLD
            #"truck": ["truck1", "truck2", "truck3", "truck4", "truck5"],
            #"driver": ["driver1", "driver2", "driver3", "driver4", "driver5"],
            #"obj": ["package1", "package2", "package3", "package4", "package5", "package6", "package7", "package8", "package9", "package10", "package11", "package12", "package13", "package14", "package15", "package16", "package17", "package18", "package19", "package20"],
            #"location": ["s0", "s1", "s2", "s3", "s4", "p0", "p1","p2", "p3", "p4", "p5", "p6", "p7", "p8","p9", "p10", "p11", "p12", "p13", "p14", "p15", "p16","p17", "p18", "p19", "p20"],
            #"p_location": ["p0", "p1", "p2", "p3", "p4", "p5", "p6", "p7","p8", "p9", "p10", "p11", "p12", "p13", "p14", "p15","p16", "p17", "p18", "p19", "p20"],
            #"s_location": ["s0", "s1", "s2", "s3", "s4"],

            },
    "logistics":
        {   
            # da obj0 a obj14
            "package": ["obj0", "obj1", "obj2", "obj3", "obj4", "obj5", "obj6", "obj7", "obj8", "obj9", "obj10", "obj11", "obj12", "obj13", "obj14", "obj15", "obj15", "obj17"],
            # da apn0 a apn9
            "airplane": ["apn0", "apn1", "apn2", "apn3", "apn4", "apn5", "apn6", "apn7",],
            "airport": ["apt0", "apt1", "apt2", "apt3", "apt4", "apt5", "apt6", "apt7", "apt8", "apt9"],
            "truck": ["tru0", "tru1", "tru2", "tru3", "tru4", "tru5", "tru6", "tru7", "tru8", "tru9"],
            "city": ["cit0", "cit1", "cit2", "cit3", "cit4", "cit5", "cit6", "cit7", "cit8", "cit9"],
            # pos da 0 fino a 39
            "location": [#"apt0", "apt1", "apt2", "apt3", "apt4", "apt5", "apt6", "apt7", "apt8", "apt9",
             "pos0", "pos1", "pos2", "pos3", "pos4", "pos5", "pos6", "pos7", "pos8", "pos9", "pos10", "pos11", "pos12", "pos13", "pos14", "pos15", "pos16", "pos17", "pos18", "pos19",],
        },
    "sokoban":
        {
            #box0 a box4
            "box": ["box0", "box1", "box2", "box3", "box4"],
            "dir" : ["up", "down", "left", "right"],
            "loc" : []
        },
    "floortile":
        {#da tile-0-1 a tile-0-7 e da tile-1-1 a tile-1-7 ... fino a tile-7-7
            "tile": ["tile-0-1", "tile-0-2", "tile-0-3", "tile-0-4", "tile-0-5", "tile-0-6", "tile-0-7",
                    "tile-1-1", "tile-1-2", "tile-1-3", "tile-1-4", "tile-1-5", "tile-1-6", "tile-1-7",
                    "tile-2-1", "tile-2-2", "tile-2-3", "tile-2-4", "tile-2-5", "tile-2-6", "tile-2-7",
                    "tile-3-1", "tile-3-2", "tile-3-3", "tile-3-4", "tile-3-5", "tile-3-6", "tile-3-7",
                    "tile-4-1", "tile-4-2", "tile-4-3", "tile-4-4", "tile-4-5", "tile-4-6", "tile-4-7",
                    "tile-5-1", "tile-5-2", "tile-5-3", "tile-5-4", "tile-5-5", "tile-5-6", "tile-5-7",
                    "tile-6-1", "tile-6-2", "tile-6-3", "tile-6-4", "tile-6-5", "tile-6-6", "tile-6-7",
                    "tile-7-1", "tile-7-2", "tile-7-3", "tile-7-4", "tile-7-5", "tile-7-6", "tile-7-7"],
            "robot": ["robot1", "robot2", "robot3", "robot4", "robot5", "robot6", "robot7"],
            "color" : ["black", "white"]
            
        },
    "visitall":
        {   # Si arriva al massimo a griglie 10x10
            "place": [  "loc-x0-y0", "loc-x0-y1", "loc-x0-y2", "loc-x0-y3", "loc-x0-y4", "loc-x0-y5", "loc-x0-y6", "loc-x0-y7", "loc-x0-y8", "loc-x0-y9", "loc-x0-y10",
                        "loc-x1-y0", "loc-x1-y1", "loc-x1-y2", "loc-x1-y3", "loc-x1-y4", "loc-x1-y5", "loc-x1-y6", "loc-x1-y7", "loc-x1-y8", "loc-x1-y9", "loc-x1-y10",
                        "loc-x2-y0","loc-x2-y1", "loc-x2-y2", "loc-x2-y3", "loc-x2-y4", "loc-x2-y5", "loc-x2-y6", "loc-x2-y7", "loc-x2-y8", "loc-x2-y9", "loc-x2-y10",
                        "loc-x3-y0", "loc-x3-y1", "loc-x3-y2", "loc-x3-y3", "loc-x3-y4", "loc-x3-y5", "loc-x3-y6", "loc-x3-y7", "loc-x3-y8", "loc-x3-y9", "loc-x3-y10",
                        "loc-x4-y0", "loc-x4-y1", "loc-x4-y2", "loc-x4-y3", "loc-x4-y4", "loc-x4-y5", "loc-x4-y6", "loc-x4-y7", "loc-x4-y8", "loc-x4-y9", "loc-x4-y10",
                        "loc-x5-y0", "loc-x5-y1", "loc-x5-y2", "loc-x5-y3", "loc-x5-y4", "loc-x5-y5", "loc-x5-y6", "loc-x5-y7", "loc-x5-y8", "loc-x5-y9", "loc-x5-y10",
                        "loc-x6-y0", "loc-x6-y1", "loc-x6-y2", "loc-x6-y3", "loc-x6-y4", "loc-x6-y5", "loc-x6-y6", "loc-x6-y7", "loc-x6-y8", "loc-x6-y9", "loc-x6-y10",
                        "loc-x7-y0", "loc-x7-y1", "loc-x7-y2", "loc-x7-y3", "loc-x7-y4", "loc-x7-y5", "loc-x7-y6", "loc-x7-y7", "loc-x7-y8", "loc-x7-y9", "loc-x7-y10",
                        "loc-x8-y0", "loc-x8-y1", "loc-x8-y2", "loc-x8-y3", "loc-x8-y4", "loc-x8-y5", "loc-x8-y6", "loc-x8-y7", "loc-x8-y8", "loc-x8-y9", "loc-x8-y10",
                        "loc-x9-y0", "loc-x9-y1", "loc-x9-y2", "loc-x9-y3", "loc-x9-y4", "loc-x9-y5", "loc-x9-y6", "loc-x9-y7", "loc-x9-y8", "loc-x9-y9", "loc-x9-y10",
                        "loc-x10-y0", "loc-x10-y1", "loc-x10-y2", "loc-x10-y3", "loc-x10-y4", "loc-x10-y5", "loc-x10-y6", "loc-x10-y7", "loc-x10-y8", "loc-x10-y9", "loc-x10-y10", 
                      ]
        }
}

def construct_object_dict(initial_state, domain):
    if domain == "blocksworld":
        initial_states = initial_state.split()
    else:
        initial_states = metric.unite_actions(initial_state, list(metric.dict_predicates_domain[domain].keys()), domain)  
    obj_dict = {}
    for i in initial_states:
        id = i.split("_")[0]
        if id in types_identifiers[domain]:
            if not id in obj_dict:
                obj_dict[id] = [i.split("_")[1]]
            else:
                obj_dict[id].append(i.split("_")[1])
    if domain == "logistics":
        # tolgo gli aeroporti dalle locations
        obj_dict["location"] = [x for x in obj_dict["location"] if not x.startswith("apt")] 
    if domain == "driverlog":
        obj_dict["p_location"] = [x for x in obj_dict["location"] if x.startswith("p")]
        obj_dict["s_location"] = [x for x in obj_dict["location"] if x.startswith("s")]
        obj_dict.pop("location")
    return obj_dict

# Cerca gli oggetti
def find_words_with_numbers(input_string):
    words = input_string.split()
    output_dict = {}

    for word in words:
        # Utilizza una espressione regolare per trovare le parole con i numeri
        matches = re.findall(r'([A-Za-z]+)(\d+)', word)
        if matches:
            # Estraggo la parte della parola senza il numero
            base_word = matches[0][0]
            # Aggiungo la parola alla lista nel dizionario senza duplicati
            if base_word not in output_dict:
                output_dict[base_word] = []
            if word not in output_dict[base_word]:
                output_dict[base_word].append(word)

    return output_dict
# Randomizza gli oggetti fra due liste
def randomize_objects(instance_dict, objects_dict):
    # Dizionario risultante
    try:
        result_dict = {}
        # Associo casualmente oggetti dai due dizionari
        for key1, values1 in instance_dict.items():
            values2 = objects_dict.get(key1, []).copy()  # Ottiengo la lista corrispondente dal secondo dizionario
            # Associo casualmente oggetti
            for value1 in values1:
                if values2 == []:
                    break
                value2 = random.choice(values2)
                result_dict[value1] = value2
                values2.remove(value2)  # Rimuovo l'oggetto utilizzato dal secondo dizionario
    except Exception as e:
        logger.error(e)
        logger.error(instance_dict)
        logger.error(objects_dict)
        return e
    return result_dict
# Replace oggetti

def replace_objects(list_predicates, object_dict):
    # TODO RIFAI QUESTA PARTE!
    risultato = []
    for i, predicato in enumerate(list_predicates):
        splitted_predicato = predicato.split()
        tmp = splitted_predicato[0]
        for p in splitted_predicato[1:]:
            if p in object_dict:
                tmp = tmp + " " + object_dict[p]
            else:
                tmp = tmp + " " + p
        risultato.append(tmp)
    return risultato

# Estrae stato iniziale e goal dal PDDL
def extract_initial_state_and_goals(pddl_problem_file, domain, typed=True, sorted_assignment=False):
    with open(pddl_problem_file, "r") as f:
        lines = f.readlines()
    lines = [line.strip().replace("(", "").replace(")", "").replace(' and', '') for line in lines]
    lines = [x.lower() for x in lines if x != '']
        
    init_index = [lines.index(line) for line in lines if ":init" in line][0]
    goal_index = [lines.index(line) for line in lines if ":goal" in line][0]
    if typed:
        # E' tipizzato allora devo recuperare dal PDDL i tipi
        obj_index = [lines.index(line) for line in lines if ":objects" in line][0]
        # Recupero gli oggetti
        objects = lines[obj_index:init_index]
        # Replace di :objects   
        objects = [x.replace(":objects", "") for x in objects]
        objects = [x for x in objects if x != '']
        if domain == "blocksworld":
            objects = " ".join(objects)
            blocks = []
            for word in objects.split():
                blocks.append(f"block_{word}")
            objects = blocks
        else:
            obj_result = []
            obj_lines_accumulator = ""
            for obj_line in objects:
                if ' - ' in obj_line:
                    obj_lines_accumulator = obj_lines_accumulator + obj_line
                    obj, predicate = obj_lines_accumulator.split(' - ')
                    obj = obj.split()
                    predicate = predicate.strip()
                    for o in obj:
                        o = o.strip()
                        obj_result.append(f'{predicate} {o}')
                    obj_lines_accumulator = ""
                else:
                    obj_lines_accumulator = obj_lines_accumulator + obj_line + " "
            objects = obj_result

    init = lines[init_index:goal_index]
    init = [x.replace(":init", "") for x in init]
    init = [x for x in init if x != '']
    goal = lines[goal_index:]
    goal = [x.replace(":goal", "").replace("and", "") for x in goal]
    goal = [x.strip() for x in goal if x != '']
    if domain == "blocksworld":
        init = list(set(init))
        goal = list(set(goal))
        return init, goal, blocks
    if typed: 
        init = list(set(init + objects))
        goal = list(set(goal))
        return init, goal
    else:
        init = list(set(init))
        goal = list(set(goal))
        return init, goal
            
def get_plan_for_problem(pddl_problem_file, domain="logistics", typed_domain=True, randomize=False, verbose = False, sorted_assignment=False):
    if domain == "blocksworld":
        initial_state, goals, blocks = extract_initial_state_and_goals(pddl_problem_file, domain, typed_domain)
        logger.info(f'Blocks: {blocks}')
    else:
        initial_state, goals = extract_initial_state_and_goals(pddl_problem_file, domain, typed_domain)

    logger.info(f'Initial state: {initial_state}')
    logger.info(f'Goals: {goals}')
    # Correggo errori eventuali nel parsing
    initial_state, goals, _ = parse_problem(initial_state, goals, [], domain)
    initial_state = metric.unite_actions(" ".join(initial_state), list(metric.dict_predicates_domain[domain].keys()), domain)
    initial_state = [x.replace("_", " ") for x in initial_state]
    goals = metric.unite_actions(" ".join(goals), list(metric.dict_predicates_domain[domain].keys()), domain)
    goals = [x.replace("_", " ") for x in goals]

    initial_state = sorted(initial_state)
    goals = sorted(goals)
    logger.info(f'Initial state: {initial_state}')
    logger.info(f'Goals: {goals}')
    # Recupero gli oggetti dallo stato iniziale
    # N.B. Nel caso di blocksworld nel leggere il PDDL mi costruisco una string apposita 
    # che contiene tutti i blocchi e parso quella per avere i nomi dei blocchi il resto è uguale
    if domain == "blocksworld":
        object_dict = construct_object_dict(" ".join(blocks), domain)
    else:
        #Caso tradizionale: i predicati che descrivono i tipi li trovo nello stato iniziale
        object_dict = construct_object_dict(" ".join(initial_state), domain)
    
    possible_objects = copy.deepcopy(objects_from_tokenizer[domain])
    logger.info(" ")
    logger.info(" ")

    logger.info(f'Object dict: {object_dict}')
    logger.info(f'Possible objects: {possible_objects}')

    # Verifico se è necessario utilizzare la tabella di conversione: controllo prima il numero di oggetti per tipo nel problema
    for type_obj in object_dict.keys():
        current_len = len(object_dict[type_obj])
        if current_len > len(possible_objects[type_obj]):
            logger.info(f"{type_obj} {current_len} {len(possible_objects[type_obj])}")
            logger.info(f"{type_obj}, Oggetti nel problema: {current_len}, Numero di oggetti disponibili: {len(possible_objects[type_obj])}")
            logger.error('Attenzione: il numero di oggetti per tipo nel problema è maggiore di quello nel vocabolario! Impossibile proseguire')
            return -1
    # Ora verifico gli oggetti effettivi -> tabella di conversione 
    if not sorted_assignment:
        to_change_vocabs = {}
        logger.info(f'Assegnazione randomica degli oggetti non presenti nel vocabolario')
        already_used = {}
        for k, x in object_dict.items():
            for obj in x:
                if not obj in possible_objects[k]:
                    logger.error(f'Attenzione: {obj} non è presente nel vocabolario! Si usi la tabella di conversione')
                    if k in to_change_vocabs:
                        to_change_vocabs[k].append(obj)
                    else:
                        to_change_vocabs[k] = [obj] 
                else:
                    if k in already_used:
                        already_used[k].append(obj)
                    else:
                        already_used[k] = [obj]
        
        logger.info("#"*50)
        logger.info(f'Cambio vocabolario')
        #Se devo modificare almeno un oggetto...
        if len(to_change_vocabs) > 0:
            # Sostituisco gli oggetti con quelli randomizzati
            destination_dict = {}
            for k in possible_objects.keys():
                if k in already_used.keys():
                    destination_dict[k] = list(set(possible_objects[k]) - set(already_used[k]))
                else:
                    destination_dict[k] = possible_objects[k]
            logger.info(f"\nTo_change_vocabs: {to_change_vocabs}")
            logger.info(f"\nDestination_dict: {destination_dict}")
            result_dict = randomize_objects(to_change_vocabs, destination_dict.copy())
            logger.info(f"\nChange_vocab dict: {result_dict}")
            initial_state = replace_objects(initial_state, result_dict)
            if domain == "blocksworld":
                blocks = [b.replace("_", " ") for b in blocks]
                blocks = replace_objects(blocks, result_dict)
                logger.info(f'Blocks: {blocks}')
                blocks = [b.replace(" ", "_") for b in blocks]
            goals = replace_objects(goals, result_dict)
        
        logger.info("#"*50)

        # Avendo cambiato lo stato iniziale cambia l'object_dict
        if domain == "blocksworld":
            object_dict = construct_object_dict(" ".join(blocks), domain)
        else:
            object_dict = construct_object_dict(" ".join(initial_state), domain)
    else:
        # Invece di assegnare casualmente i nomi agli oggetti li assegno in ordine
        result_dict = {}
        logger.info('Sovrascrittura nomi oggetti - Sorted assignment')
        for k in object_dict.keys():
            for i, obj in enumerate(sorted(object_dict[k])):
                result_dict[obj] = possible_objects[k][i]
        logger.info(f'Change_vocab dict: {result_dict}')
        initial_state = replace_objects(initial_state, result_dict)
        goals = replace_objects(goals, result_dict)
        logger.info(f'Initial state sovrascritto: {initial_state}')
        logger.info(f'Goals sovrascritti: {goals}')
        if domain == "blocksworld":
            blocks = [b.replace("_", " ") for b in blocks]
            blocks = replace_objects(blocks, result_dict)
            logger.info(f'Blocks: {blocks}')
            blocks = [b.replace(" ", "_") for b in blocks]
            object_dict = construct_object_dict(" ".join(blocks), domain)
        else:
            object_dict = construct_object_dict(" ".join(initial_state), domain)


    # Eventuale randomizzazione
    if randomize:
        logger.info(f'Randomize')
        logger.info(f'\nInitial state: {initial_state}')
        logger.info(" ")
        logger.info(f"Goals: {goals}")
        possible_objects = copy.deepcopy(objects_from_tokenizer[domain])
        random_dict = possible_objects.copy()

        '''for k in possible_objects.keys():
            if k in object_dict:
                for obj in object_dict[k]:
                    continue
                else:
                    random_dict[k] = list(set(possible_objects[k]) - set(object_dict[k]))'''
        logger.info(" ")
        logger.info(f'Possible objects for randomize: {possible_objects}')
        # Sostituisco gli oggetti con quelli randomizzati
        result_dict = randomize_objects(object_dict, random_dict)
        logger.info(f'Result dict randomize: {result_dict}')
        initial_state = replace_objects(initial_state, result_dict)
        goals = replace_objects(goals, result_dict)
        logger.info(" ")
        logger.info(f'Initial state randomizzato: {initial_state}')
        logger.info(f'Goals randomizzati: {goals}')

            
    initial_state = [i.replace("_", " ") for i in initial_state]
    initial_state = sorted(initial_state)
    goals = [i.replace("_", " ") for i in goals]
    goals = sorted(goals)
    if domain == "driverlog" or domain == "floortile":
        # Modifica per fare funzionare blocksworld...
        initial_state = [i.replace(" ", "_") for i in initial_state]
        goals = [i.replace(" ", "_") for i in goals]
        initial_state = sorted(initial_state)
        initial_state = [i.replace("_", " ") for i in initial_state]
        goals = sorted(goals)
        goals = [i.replace("_", " ") for i in goals]
    initial_state = " ".join(initial_state)
    goals = " ".join(goals)
    #initial_state = " ".join(initial_state)
    #goals = " ".join(goals)
    #logger.info(f'Dominio {domain}')
    #logger.info(f'Stato iniziale {initial_state}')
    #logger.info(f'Goal {goals}')
    

    formatted_string = initial_state + " <|goals|> " + goals + " <|actions|> "
    # Costruita la stringa da tokenizzare
    # Recuperare modello e tokenizzatore
    #logger.info(f'Stringa da tokenizzare: {formatted_string}')
    return formatted_string


def main():
    # Parsing delle opzioni
    parser = HfArgumentParser(SolvingPDDLArgs)
    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        (args,) = parser.parse_json_file(json_file=os.path.abspath(sys.argv[1]))
    else:
        (args,) = parser.parse_args_into_dataclasses()
    logger.info(args)
    plan_output_dir = Path(args.output_dir)
    plan_output_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = plan_output_dir.joinpath(args.log_file_name)
    with open(log_file_path, "w") as f:
        f.write("")
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file_path),
        ],
    )    
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer_dir)
    logger.info(tokenizer)
    model = GPT2PModel.from_pretrained(args.model_dir, device_map="auto", pad_token_id=tokenizer.pad_token_id)
    logger.info(model)
    model.to("cuda")
    
    problems = os.listdir(args.pddl_dir)
       
    problems = [x for x in problems if x.endswith(".pddl")]

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    results = {}
    logger.info(f'Recuperati i {len(problems)} problemi da risolvere')
    counter = 0
    problems_analized = len(problems)
    error_problems = []
    problems = sorted(problems)
    for problem in tqdm(problems):
        logger.info("-"*50)
        starting_time = time.time()
        logger.info(f'Problema {problem}')
        problem_path = args.pddl_dir + problem
        formatted_string = get_plan_for_problem(problem_path, 
                                            domain=args.domain, 
                                            typed_domain=args.typed_domain, 
                                            randomize=args.randomize,
                                            sorted_assignment=args.sorted_assignment,)
        '''except Exception as e:
            logger.info(f'Errore nel parsing del problema {problem}')
            logger.info(e)
            problems_analized -= 1
            continue
        '''
        # Tokenizzare la stringa
        if formatted_string == -1:
            logger.info(f"Errore nel problema {problem}")
            error_problems.append(problem)
            logger.info('Impossibile proseguire')
            problems_analized -= 1
            continue
        tokenized_string = tokenizer(formatted_string, return_token_type_ids=False, return_tensors="pt", )
        logger.info(f'\nStringa da tokenizzare: {formatted_string}')
        logger.info(f'Stringa tokenizzata: {tokenizer.decode(tokenized_string["input_ids"][0])}')
        # Generare la sequenza
        input_ids = tokenized_string['input_ids']
        input_ids = input_ids.to("cuda")
        generated_sequence = model.generate(input_ids, 
                                            max_length=args.max_length, 
                                            num_beams=args.num_beams,
                                            num_return_sequences=args.num_return_sequences,
                                            top_k=args.top_k,
                                            top_p=args.top_p,
                                            do_sample=args.do_sample,
                                            pad_token_id=tokenizer.pad_token_id, 
                                            eos_token_id=tokenizer.eos_token_id,)
        ending_time = time.time()
        action_id_token = tokenizer.convert_tokens_to_ids("<|actions|>")
        # Cerchiamo l'action_idx
        if args.num_return_sequences > 1:
            correct_plan = None
            for seq in range(args.num_return_sequences):
                action_idx = generated_sequence[seq].tolist().index(action_id_token)
                plan = generated_sequence[seq][action_idx + 1:]
                plan = tokenizer.decode(plan, skip_special_tokens=True)
                tmp_plan = {}
                tmp_plan['input'] = '<|startofplan|> ' + formatted_string
                tmp_plan['actions'] = plan
                result = metric.parse_problem(tmp_plan, args.domain)
                tmp_plan['result'] = result
                logger.info(f'Generata traccia {seq}')
                logger.info(f'Input: {tmp_plan["input"]}')
                logger.info(f'Action ID token: {tokenizer.decode(generated_sequence[seq][action_idx])}')
                logger.info(f'Piano generato: {plan}')
                logger.info(f'Risultato: {result}') 
                if result[0] is True:   
                    if correct_plan is None:
                        correct_plan = tmp_plan
                    elif len(correct_plan['actions']) > len(plan):
                        correct_plan = tmp_plan
            if correct_plan is None:
                tmp_plan['time'] = ending_time - starting_time
                results[problem] = tmp_plan
                logger.info(f'Multibeam NON ha raggiunto un piano corretto')
                logger.info(f'Input: {tmp_plan["input"]}')
                logger.info(f'Piano generato: {plan}')
                logger.info(f'Risultato: {result}')
                # Non incremento il contat  ore perchè non avrò trovato piani positivi
            else:
                correct_plan['time'] = ending_time - starting_time
                results[problem] = correct_plan
                logger.info(f'Multibeam ha raggiunto un piano corretto')
                logger.info(f'Input: {tmp_plan["input"]}')
                logger.info(f'Piano generato: {correct_plan["actions"]}')
                logger.info(f'Risultato: {correct_plan["result"]}')
                counter += 1
        else:
            action_idx = generated_sequence[0].tolist().index(action_id_token)
            plan = generated_sequence[0][action_idx + 1:]
            plan = tokenizer.decode(plan, skip_special_tokens=True)
            
            tmp_plan = {}
            tmp_plan['input'] = '<|startofplan|> ' + formatted_string
            tmp_plan['actions'] = plan
            tmp_plan['time'] = ending_time - starting_time
            result = metric.parse_problem(tmp_plan, args.domain)
            tmp_plan['result'] = result
            results[problem] = tmp_plan
            if result[0] is True:
                counter += 1
            logger.info(f'Piano generato: {plan}')
            logger.info(f'Input: {tmp_plan["input"]}')
            logger.info(f'Risultato: {result}')
    logger.info(f'Piani totali: {len(problems)}')
    logger.info(f'Piani analizzati: {problems_analized}')
    logger.info(f'Piani errati: {error_problems}')
    logger.info(f'Piani con goals raggiunti senza violazione precondizioni  : {counter}')
    logger.info(f'Piani validi: {counter/problems_analized*100.0}%')
    with open(args.output_dir + "results.json", "w") as f:
        json.dump(dict(sorted(results.items())), f, indent=4)

if __name__ == "__main__":
    main()