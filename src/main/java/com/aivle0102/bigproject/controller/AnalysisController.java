package com.aivle0102.bigproject.controller;

import com.aivle0102.bigproject.client.AnalysisServiceClient;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/analysis")
@RequiredArgsConstructor
public class AnalysisController {

    private final AnalysisServiceClient analysisServiceClient;

    @GetMapping
    @Cacheable(value = "analysis", key = "#country + '-' + #item")
    public Mono<Object> getAnalysis(
            @RequestParam String country,
            @RequestParam String item) {
        return analysisServiceClient.getAnalysis(country, item);
    }
}
